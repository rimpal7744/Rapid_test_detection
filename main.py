from fastapi import FastAPI, File, UploadFile
import uvicorn
import os
import uuid
from extraction import main
app = FastAPI()

#uploading file and get results
@app.post("/upload-file/")
async def create_upload_file(file: UploadFile = File(...)):
    end_name=(file.filename).split('.')[-1]
    file_location = f"{(str(uuid.uuid1())+str(end_name))}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    try:
        final_result=main(file_location)
    except Exception as e:
        final_result={}

    if final_result=={}:
        final_result={'Invalid Image'}

    os.remove(file_location)

    return final_result



# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=6000)