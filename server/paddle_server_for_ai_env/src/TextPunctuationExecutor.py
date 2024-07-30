from paddlespeech.cli.text import TextExecutor
from typing import Optional
import paddle
import os


class TextPunctuationExecutor(TextExecutor):
    def __init__(self):
        super().__init__()

    def init(self,
            task: str = 'punc',
            model_type: str = 'ernie_linear_p7_wudao',
            lang: str = 'zh',
            cfg_path: Optional[os.PathLike] = None,
            ckpt_path: Optional[os.PathLike] = None,
            vocab_file: Optional[os.PathLike] = None):
        if model_type in ['ernie_linear_p7_wudao', 'ernie_linear_p3_wudao']:
            self._init_from_path(task, model_type, lang, cfg_path, ckpt_path, vocab_file)
        else:
            self._init_from_path_new(task, model_type, lang, cfg_path, ckpt_path, vocab_file)

    def __call__(self,
                 text: str,
                 task: str = 'punc',
                 model: str = 'ernie_linear_p7_wudao',
                 lang: str = 'zh',
                 config: Optional[os.PathLike] = None,
                 ckpt_path: Optional[os.PathLike] = None,
                 punc_vocab: Optional[os.PathLike] = None,
                 device: str = paddle.get_device(), ):
        """
                Python API to call an executor.
                """
        return super().__call__(text, task, model, lang, config, ckpt_path, punc_vocab, device)
