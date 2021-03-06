# python demo.py --image_folder "C:/Users/Jamie/Documents/University-Stuffs/Research/project/data/JPEGImages" --loop --vis
# python demo.py --images "C:/Users/Jamie/Desktop/zxy.jpg" --loop --vis
import glob
import tqdm
import cv2
import argparse
import numpy as np
import torch

import human_det
# this can be install by:
# pip install git+https://github.com/Project-Splinter/streamer_pytorch --upgrade
import streamer_pytorch as streamer


parser = argparse.ArgumentParser(description='.')
parser.add_argument(
    '--camera', action="store_true", help="whether to use webcam.")
parser.add_argument(
    '--images', default="", nargs="*", help="paths of image.")
parser.add_argument(
    '--image_folder', default=None, help="path of image folder.")
parser.add_argument(
    '--videos', default="", nargs="*", help="paths of video.")
parser.add_argument(
    '--loop', action="store_true", help="whether to repeat images/video.")
parser.add_argument(
    '--vis', action="store_true", help="whether to visualize.")
args = parser.parse_args()

def draw_bboxes(window, bboxes, probs):
    bboxes = bboxes.view(-1, 1, 4).squeeze().cpu().numpy()
    for bbox in bboxes:
        window = cv2.rectangle(
            window,
            (int(bbox[0]), int(bbox[1])),
            (int(bbox[2]), int(bbox[3])),
            (255, 0, 0), 2)


def visulization(data):
    image, bboxes, probs = data
    print(probs)

    #probs = probs.unsqueeze(3)
    #print(bboxes, probs, '\n')
    #bboxes = (bboxes * probs).sum(dim=1, keepdim=True) / probs.sum(dim=1, keepdim=True)
    #print(bboxes, probs)


    window = image[0].cpu().numpy().transpose(1, 2, 0)
    window = (window * 0.5 + 0.5) * 255.0
    window = np.uint8(window).copy()

    # bbox = bboxes[0, 0, 0].cpu().numpy()
    # window = cv2.rectangle(
    #     window,
    #     (int(bbox[0]), int(bbox[1])),
    #     (int(bbox[2]), int(bbox[3])),
    #     (255,0,0), 2)
    #
    draw_bboxes(window, bboxes, probs)

    window = cv2.cvtColor(window, cv2.COLOR_BGR2RGB)
    window = cv2.resize(window, (0, 0), fx=2, fy=2)
    #
    cv2.imshow('window', window)
    cv2.waitKey(1)


det_engine = human_det.Detection()


if args.camera:
    data_stream = streamer.CaptureStreamer(pad=False)
elif len(args.videos) > 0:
    data_stream = streamer.VideoListStreamer(
        args.videos * (10 if args.loop else 1))
elif len(args.images) > 0:
    data_stream = streamer.ImageListStreamer(
        args.images * (10000 if args.loop else 1))
elif args.image_folder is not None:
    images = sorted(glob.glob(args.image_folder+'/*.jpg'))
    images += sorted(glob.glob(args.image_folder+'/*.png'))
    data_stream = streamer.ImageListStreamer(
        images * (10 if args.loop else 1))


loader = torch.utils.data.DataLoader(
    data_stream, 
    batch_size=1, 
    num_workers=0,
    pin_memory=False,
)


try:
    # no vis: ~ 70 fps
    for data in loader:
        bboxes, probs = det_engine(data)
        if args.vis:
            visulization([data, bboxes, probs])
except Exception as e:
    print (e)
    del data_stream
