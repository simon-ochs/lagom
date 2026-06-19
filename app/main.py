import logging
import zipfile

from fastapi import FastAPI, Form, HTTPException, UploadFile

from app import analysis, loader
from app.models import AnalysisResult, PumpConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("lagom")

app = FastAPI(title="Lagom", description="Omnipod 5 bolus ratio analysis")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalysisResult)
async def analyze(file: UploadFile, config: str = Form("{}")):
    """Analyze a Glooko export zip and return ISF/ICR recommendations.

    `config` is a JSON-encoded PumpConfig, e.g. {"icr": 10, "isf": 30, "target_glucose": 110}.
    """
    pump = PumpConfig.model_validate_json(config)
    logger.info("Analyzing '%s' against ICR=%s ISF=%s target=%s",
                file.filename, pump.icr, pump.isf, pump.target_glucose)

    zip_bytes = await file.read()
    try:
        frames = loader.load_glooko_zip(zip_bytes)
    except (KeyError, zipfile.BadZipFile) as e:
        logger.warning("Rejected upload '%s': %s", file.filename, e)
        raise HTTPException(status_code=400, detail=f"Invalid Glooko export: {e}")

    result = analysis.run_analysis(*frames, pump)
    logger.info("Analysis complete for '%s'", file.filename)
    return result
