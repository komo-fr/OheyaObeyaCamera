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
logger.setLevel(logging.DEBUG)
s_handler = logging.StreamHandler()
log_format = '[%(levelname)s][%(asctime)s] %(message)s'
formatter = logging.Formatter(log_format)
s_handler.setFormatter(formatter)
logger.addHandler(s_handler)


class OheyaObeyaError(Exception):
    "Apprlication Error"


def main(n_repeat: int = 1, level: str = None, n_interval: int = 5) -> None:
    n_repeat = 1 if not n_repeat else n_repeat
    logger.debug('Level: {}'.format(level))

    pygame.mixer.init()

    # 実際には以下のサイトから素材を借りた
    # 効果音ラボ: https://soundeffect-lab.info/sound/button/
    # ※ 再配布不可なのでGitHub上には音源ファイルはuploadしていない
    #   使用する際は指定のパスに適当な音源を配置すること
    pygame.mixer.music.load(str(Path(SOUND_ROOT_PATH) / 'start.mp3'))
    pygame.mixer.music.play(1)

    for i in range(0, n_repeat):
        try:
            capture(level)
            pygame.mixer.music.load(str(Path(SOUND_ROOT_PATH) / 'sf.wav'))
            pygame.mixer.music.play(1)
            logger.info(str(i))
            time.sleep(1)

        except OheyaObeyaError:
            import traceback
            traceback.print_exc()
            pygame.mixer.music.load(str(Path(SOUND_ROOT_PATH) / 'error.mp3'))
            pygame.mixer.music.play(1)
            time.sleep(2)
            pygame.mixer.music.stop()
            return

        if i < n_repeat - 1:
            for _ in range(0, n_interval):
                pygame.mixer.music.load(str(Path(SOUND_ROOT_PATH) / 'count.wav'))
                pygame.mixer.music.play(1)
                time.sleep(1)

    pygame.mixer.music.load(str(Path(SOUND_ROOT_PATH) / SETTINGS['end_sound']))
    pygame.mixer.music.play(1)
    time.sleep(2)
    pygame.mixer.music.stop()


def capture(level: str = None) -> None:
    n_images = 0

    # capture
    for i in range(0, 4):
        cap = cv2.VideoCapture(i)
        image = cap.read()[1]

        # 想定しているUSBカメラで撮影しているかのチェック
        # たまに変わるので暫定で入れているが、多分もっといい方法がある
        if image is None:
            logger.info('Camera {} is skipped.'.format(i))
            cap.release()
            continue

        logger.debug('camera {}: {}'.format(i, image.shape))

        if image.shape == settings.CAMERA_RAW_SIZE:
            # save
            file_name = dt.now().strftime("%Y%m%d_%H%M%S_{camera_id}_{level}.jpg".format(camera_id=i, level=level))
            time.sleep(0.5)
            dir_name = 'unknown' if not level else level
            path = Path(SETTINGS['data_root_path']) / 'images' / dir_name / str(i) / file_name
            path.parent.mkdir(exist_ok=True, parents=True)
            cv2.imwrite(str(path), image)
            logger.info('Save: {}'.format(path))
            n_images += 1

        cap.release()

    if n_images == 0:
        message = 'Failed to capture. Not found an expected camera.'
        raise OheyaObeyaError(message)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='capture.py',
                                     add_help=True)
    parser.add_argument('-p', '--prod', help='本番用',
                        action='store_true')
    parser.add_argument('-l', '--level',
                        help='汚さの度合いを1-5またはclean or dirtyで指定する（数字の場合、大きい方が汚い）')
    parser.add_argument('-r', '--repeat',
                        help='連続撮影モード', type=int)
    parser.add_argument('-i', '--interval',
                        help='連続撮影モードにおける撮影と撮影のインターバル', type=int)
    args = parser.parse_args()

    logger.info('Start.')

    if args.prod:
        SETTINGS = settings.PROD_SETTINGS
        logger.info('mode = prod')
    else:
        SETTINGS = settings.DEV_SETTINGS
        logger.info('mode = dev')

    main(args.repeat, args.level, args.interval)
    logger.info('Completed.')
