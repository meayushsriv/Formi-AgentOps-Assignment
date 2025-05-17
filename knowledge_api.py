from fastapi import FastAPI, HTTPException
import pandas as pd
import os
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI()

class FilterRequest(BaseModel):
    primary_name: str
    source: str
    additional_filters: Optional[List[dict]] = None

@app.post("/api/filter")
async def filter_information(request: FilterRequest):
    try:
        if not request.primary_name or not request.source:
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        file_path = f"data/{request.source}.csv"
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Data file not found")
        
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")
        
        filtered_df = df[df['primary_name'] == request.primary_name]
        
        if request.additional_filters:
            for filter in request.additional_filters:
                if 'column_name' not in filter or 'value' not in filter:
                    continue
                filtered_df = filtered_df[filtered_df[filter['column_name']] == filter['value']]
        
        result = filtered_df.to_dict(orient='records')
        chunk_size = 5 
        chunks = [result[i:i + chunk_size] for i in range(0, len(result), chunk_size)]
        
        return {
            "data": chunks[0] if chunks else [],
            "total_chunks": len(chunks),
            "current_chunk": 1
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chunk/{chunk_id}")
async def get_chunk(source: str, primary_name: str, chunk_id: int):
    pass