# 语音识别
from faster_whisper import WhisperModel
import langid
model_size = "large-v2"
model = WhisperModel(model_size, device="cuda", compute_type="int8", download_root="/opt/paddle_server_for_ai_env/whisper/models")
# 翻译
import dl_translate as dlt
mt = dlt.TranslationModel()

from starlette.responses import PlainTextResponse
from fastapi import FastAPI
import numpy as np

import json
import os

from ClipIndexRequest import ClipIndexRequest
from ClipSearchRequest import ClipSearchRequest


import traceback
from VoiceToTextRequest import VoiceToTextRequest
from LangDetectRequest import LangDetectRequest
from ClipToVectorRequest import ClipToVectorRequest
from paddleocr import PaddleOCR
from OCRRequest import OCRRequest
from VectorRequest import VectorRequest
from TranslateRequest import TranslateRequest
from ppvector.predict import PPVectorPredictor
from scipy.io.wavfile import read
import torch
from PIL import Image
import cn_clip.clip as clip
from cn_clip.clip import load_from_name, available_models

print("clip Available models:", available_models())

device = "cuda" if torch.cuda.is_available() else "cpu"
clip_model, preprocess = load_from_name("ViT-B-16", device=device, download_root='./')
clip_model.eval()

# 初始化PPVector模型和配置
ppvector_predictor = PPVectorPredictor(
    configs='/opt/paddle_server_for_ai_env/ppvector/configs/ecapa_tdnn.yml',
    model_path='/opt/paddle_server_for_ai_env/ppvector/models/EcapaTdnn_Fbank/best_model/',
    use_gpu=True
)
# 初始化ocr服务
ocr = PaddleOCR(use_angle_cls=True, lang="ch", gpu_mem=1000)
# 初始化fastapi，对外提供http服务
app = FastAPI()


@app.post("/paddlespeech/asr", response_class=PlainTextResponse)
def voice_to_text(request: VoiceToTextRequest):
    try:
        print(str(request.audio))
        segments, info = model.transcribe(str(request.audio), beam_size=5, language="zh")
        print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
        texts = []
        for segment in segments:
          # print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
          texts.append(segment.text)
        return ",".join(texts)
    except Exception as msg:
        print("语音转换失败：" + str(msg))
        traceback.print_exc()
        return ""


@app.post("/paddleocr", response_class=PlainTextResponse)
def image_to_text(request: OCRRequest):
    try:
        if os.stat(request.image).st_size <= 0:
            return ""
        result = ocr.ocr(img=request.image, cls=request.cls)
        res_str = ""
        for idx in range(len(result)):
            try:
                res = result[idx]
                res_str += res[1][0]
            except Exception as e:
                traceback.print_exc()
        return res_str
    except Exception as e1:
        return ""


@app.post("/paddlespeech/vector")
def voice_to_vector(request: VectorRequest):
    # 返回音频声纹特征向量(double类型数组)
    try:
        res = ppvector_predictor.predict(request.audio_file)
        json = {
            "vector": np.array(res).tolist()
        }
        return json
    except Exception as e:
        traceback.print_exc()
        # 返回空特征
        return {"vector": []}


@app.post("/translate", response_class=PlainTextResponse)
def translate(request: TranslateRequest):
    try:
        res = mt.translate(request.text, source=request.from_lang, target=request.to_lang)
        return res
    except Exception as e:
        traceback.print_exc()
        # 返回空
        return ""

@app.post("/langdetect", response_class=PlainTextResponse)
def translate(request: LangDetectRequest):
    try:
        res = langid.classify(request.text)
        return res[0]
    except Exception as e:
        traceback.print_exc()
        # 返回空
        return ""
		
        
@app.post("/clip/to_vector")
def clip_to_vector(request: ClipToVectorRequest):
    try:
        raw_v = None
        feature_to_search = None
        # 优先处理text参数
        if request.text:
            raw_v = clip.tokenize([request.text]).to(device)
            feature_to_search = clip_model.encode_text(raw_v)
        else:
            if os.stat(request.imagePath).st_size <= 0:
                return {}
            raw_v = preprocess(Image.open(request.imagePath)).unsqueeze(0).to(device)
            feature_to_search = clip_model.encode_image(raw_v)
        with torch.no_grad():
            # 归一化
            feature_to_search /= feature_to_search.norm(dim=-1, keepdim=True)
            # 构造响应体
            f_a = feature_to_search.cpu().numpy()[0].tolist()
            data = {
                "vector": f_a
            }
            return data
    except Exception as e:
        traceback.print_exc()
        return {}
        
