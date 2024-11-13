# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved
import argparse
import glob
import multiprocessing as mp
import os
import time
import cv2
import tqdm
import numpy as np
import torch
from PIL import Image

from detectron2.data.detection_utils import read_image
from detectron2.utils.logger import setup_logger

from .predictor import VisualizationDemo
from adet.config import get_cfg

from detectron2.config import CfgNode

# constants
WINDOW_NAME = "COCO detections"


def add_custom_configs(cfg: CfgNode):
    _C = cfg
    _C.SOLVER.BEST_CHECKPOINTER = CfgNode({"ENABLED": False})
    _C.SOLVER.BEST_CHECKPOINTER.METRIC = "bbox/AP50"
    _C.SOLVER.BEST_CHECKPOINTER.MODE = "max"
    _C.TRAIN_LOG_PERIOD = 200


def setup_cfg(args):
    # load config from file and command-line arguments
    cfg = get_cfg()
    add_custom_configs(cfg)
    cfg.merge_from_file(args.config_file)
    cfg.merge_from_list(args.opts)
    # Set score_threshold for builtin models
    cfg.MODEL.RETINANET.SCORE_THRESH_TEST = args.confidence_threshold
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = args.confidence_threshold
    cfg.MODEL.FCOS.INFERENCE_TH_TEST = args.confidence_threshold
    cfg.MODEL.MEInst.INFERENCE_TH_TEST = args.confidence_threshold
    cfg.MODEL.PANOPTIC_FPN.COMBINE.INSTANCES_CONFIDENCE_THRESH = (
        args.confidence_threshold
    )
    cfg.freeze()
    return cfg


def get_parser():
    parser = argparse.ArgumentParser(description="Detectron2 Demo")
    parser.add_argument(
        "--config-file",
        default="configs/quick_schedules/e2e_mask_rcnn_R_50_FPN_inference_acc_test.yaml",
        metavar="FILE",
        help="path to config file",
    )
    parser.add_argument(
        "--webcam", action="store_true", help="Take inputs from webcam."
    )
    parser.add_argument("--video-input", help="Path to video file.")
    parser.add_argument(
        "--input", nargs="+", help="A list of space separated input images"
    )
    parser.add_argument(
        "--output",
        help="A file or directory to save output visualizations. "
        "If not given, will show output in an OpenCV window.",
    )

    parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=0.3,
        help="Minimum score for instance predictions to be shown",
    )
    parser.add_argument(
        "--opts",
        help="Modify config options using the command-line 'KEY VALUE' pairs",
        default=[],
        nargs=argparse.REMAINDER,
    )
    return parser


def crop_images(predictions, n, logger):
    imgs = os.listdir('./ABCNetv2/demo_images/test/')
    logger.info(f"log of line 89: imgs = {imgs}")
    an_onmtp_codnat = predictions["instances"]._fields["pred_boxes"].tensor
    im = Image.open(f'./ABCNetv2/demo_images/test/{imgs[n]}')

    #重複検出を削除（2つの検出対象の距離が一定以内だと片方を削除）
    dup = 0
    range_codnat = list( range( len(an_onmtp_codnat) ) )
    for k in range_codnat:
        for l in range_codnat[k+1: len(an_onmtp_codnat)-dup-1 ]:
            if an_onmtp_codnat[l,0].item():
                distance_threshold =  \
                        np.sqrt(  (an_onmtp_codnat[k,0].item() - an_onmtp_codnat[l,0].item())**2 \
                                + (an_onmtp_codnat[k,1].item() - an_onmtp_codnat[l,1].item())**2  )
                
                if distance_threshold < 30:
                    dup += 1
                    distance_areasize = \
                        ( an_onmtp_codnat[l,2].item() - an_onmtp_codnat[l,0].item() ) \
                            * ( an_onmtp_codnat[l,3].item() - an_onmtp_codnat[l,1].item() ) \
                    - ( an_onmtp_codnat[k,2].item() - an_onmtp_codnat[k,0].item() ) \
                            * ( an_onmtp_codnat[k,3].item() - an_onmtp_codnat[k,1].item() )
                    smaller = k
                    if distance_areasize < 0:
                        smaller = l

                    an_onmtp_codnat = torch.cat(  (an_onmtp_codnat[0:smaller] , an_onmtp_codnat[smaller+1:])  ,dim=0)
                    range_codnat.pop(smaller)

    logger.info( f'log of line 116: len of codnat: {len(an_onmtp_codnat)}  dup: {dup}')

    for i in range(len(an_onmtp_codnat)):   #1枚の画像の中のオノマトペを1つずつcrop
        im_crop = im.crop( ( an_onmtp_codnat[i,0].item()-6, an_onmtp_codnat[i,1].item()-6, an_onmtp_codnat[i,2].item()+6, an_onmtp_codnat[i,3].item()+6 ) )
        im_crop.save(f'./ABCNetv2/demo_results/test/{imgs[n][:-4]}_{i}.jpg', quality=95)

    onmtp_codnat = np.vectorize(int)(an_onmtp_codnat.tolist())
    return onmtp_codnat, imgs


#this is the summerized function
def main():
    mp.set_start_method("spawn", force=True)
    args, unknown = get_parser().parse_known_args()
    logger = setup_logger()
    logger.info("Arguments: " + str(args))

    cfg = setup_cfg(args)

    demo = VisualizationDemo(cfg)

    if args.input:
        if os.path.isdir(args.input[0]):
            args.input = [
                os.path.join(args.input[0], fname)
                for fname in os.listdir(args.input[0])
            ]
        elif len(args.input) == 1:
            args.input = glob.glob(os.path.expanduser(args.input[0]))
            assert args.input, "The input path(s) was not found"

        n=0
        onmtp_codnat = []
        for path in tqdm.tqdm(args.input, disable=not args.output):
            # use PIL, to be consistent with evaluation
            img = read_image(path, format="BGR")
            start_time = time.time()
            predictions, visualized_output = demo.run_on_image(img)
            logger.info(
                "{}: detected {} instances in {:.2f}s".format(
                    path, len(predictions["instances"]), time.time() - start_time
                )
            )
            
            crop_imgs = crop_images(predictions, n, logger)
            onmtp_codnat.append(crop_imgs[0])

            # make output folder here?
            os.makedirs(args.output, exist_ok=True)

            """"""
            if args.output:
                if os.path.isdir(args.output):
                    assert os.path.isdir(args.output), args.output
                    out_filename = os.path.join(args.output, os.path.basename(path))
                else:
                    assert (
                        len(args.input) == 1
                    ), "Please specify a directory with args.output"
                    out_filename = args.output

                try:
                    visualized_output.save(out_filename)
                except:
                    print("err not a image? The model is not trained enough?")

            else:
                cv2.imshow(WINDOW_NAME, visualized_output.get_image()[:, :, ::-1])
                if cv2.waitKey(0) == 27:
                    break  # esc to quit
            
            n += 1
        #logger.info(f"line of 187: onmtp_codnat = {onmtp_codnat}")

    elif args.webcam:
        assert args.input is None, "Cannot have both --input and --webcam!"
        cam = cv2.VideoCapture(0)
        for vis in tqdm.tqdm(demo.run_on_video(cam)):
            cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
            cv2.imshow(WINDOW_NAME, vis)
            if cv2.waitKey(1) == 27:
                break  # esc to quit
        cv2.destroyAllWindows()
    elif args.video_input:
        video = cv2.VideoCapture(args.video_input)
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frames_per_second = video.get(cv2.CAP_PROP_FPS)
        num_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        basename = os.path.basename(args.video_input)

        if args.output:
            if os.path.isdir(args.output):
                output_fname = os.path.join(args.output, basename)
                output_fname = os.path.splitext(output_fname)[0] + ".mkv"
            else:
                output_fname = args.output
            assert not os.path.isfile(output_fname), output_fname
            output_file = cv2.VideoWriter(
                filename=output_fname,
                # some installation of opencv may not support x264 (due to its license),
                # you can try other format (e.g. MPEG)
                fourcc=cv2.VideoWriter_fourcc(*"x264"),
                fps=float(frames_per_second),
                frameSize=(width, height),
                isColor=True,
            )
        assert os.path.isfile(args.video_input)
        for vis_frame in tqdm.tqdm(demo.run_on_video(video), total=num_frames):
            if args.output:
                output_file.write(vis_frame)
            else:
                cv2.namedWindow(basename, cv2.WINDOW_NORMAL)
                cv2.imshow(basename, vis_frame)
                if cv2.waitKey(1) == 27:
                    break  # esc to quit
        video.release()
        if args.output:
            output_file.release()
        else:
            cv2.destroyAllWindows()

    return onmtp_codnat, crop_imgs[1]



if __name__ == "__main__":
    main()
