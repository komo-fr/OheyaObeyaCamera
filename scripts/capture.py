import argparse
from datetime import datetime as dt
from pathlib import Path
import time
import logging

import cv2
import pygame.mixer

from secret import settings


PJ_ROOT_PATH = settings.PJ_ROOT_PATH
SOUND_ROOT_PATH = settings.SOUND_ROOT_PATH

# log settings
logger = logging.getLogger('OheyaObeyaCamera')
logger.setLevel(logging.INFO)
s_handler = logging.StreamHandler()
log_format = '[%(levelname)s][%(asctime)s] %(message)s'
formatter = logging.Formatter(log_format)
s_handler.setFormatter(formatter)
logger.addHandler(s_handler)


class OheyaObeyaError(Exception):
    "Apprlication Error"


def main() -> None:
    pygame.mixer.init()

    # 実際には以下のサイトから素材を借りた
    # 効果音ラボ: https://soundeffect-lab.info/sound/button/
    # ※ 再配布不可なのでGitHub上には音源ファイルはuploadしていない
    #   使用する際は指定のパスに適当な音源を配置すること
    pygame.mixer.music.load(str(Path(SOUND_ROOT_PATH) / 'start.mp3'))
    pygame.mixer.music.play(1)

    try:
        capture()
    except OheyaObeyaError:
        import traceback
        traceback.print_exc()
        pygame.mixer.music.load(str(Path(SOUND_ROOT_PATH) / 'error.mp3'))
        pygame.mixer.music.play(1)
        time.sleep(2)
        pygame.mixer.music.stop()
        return

    pygame.mixer.music.load(str(Path(SOUND_ROOT_PATH) / SETTINGS['end_sound']))
    pygame.mixer.music.play(1)
    time.sleep(2)
    pygame.mixer.music.stop()


def capture() -> None:

    # capture
    for i in range(0, 2):
        cap = cv2.VideoCapture(i)
        image = cap.read()[1]
        logger.debug('camera {}: {}'.format(i, image.shape))

        # 想定しているUSBカメラで撮影しているかのチェック
        # たまに変わるので暫定で入れているが、多分もっといい方法がある
        if image.shape == settings.CAMERA_RAW_SIZE:
            break
    else:
        message = 'Failed to capture. Not found an expected camera.'
        raise OheyaObeyaError(message)

    # save
    file_name = dt.now().strftime("%Y%m%d_%H%M%S.jpg")
    path = Path(SETTINGS['data_root_path']) / 'images' / file_name
    path.parent.mkdir(exist_ok=True, parents=True)
    cv2.imwrite(str(path), image)

    cap.release()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='capture.py',
                                     add_help=True)
    parser.add_argument('-p', '--prod', help='本番用',
                        action='store_true')
    args = parser.parse_args()

    logger.info('Start')

    if args.prod:
        SETTINGS = settings.PROD_SETTINGS
        logger.info('mode = prod')
    else:
        SETTINGS = settings.DEV_SETTINGS
        logger.info('mode = dev')

    main()
    logger.info('Completed.')
