from typing import List, Any, Optional
from pydantic import BaseModel

class Test(BaseModel):
    input: Any
    output: Any

class Code(BaseModel):
    source_code: str
    shown_tests: List[Test]
    hidden_tests: Optional[List[Test]]

class SubmitCode(BaseModel):
    question_id: int
    source_code: str
    shown_tests: List[Test]
    hidden_tests: Optional[List[Test]]
