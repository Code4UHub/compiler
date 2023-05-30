from typing import List, Any, Optional
from pydantic import BaseModel

class Test(BaseModel):
    input: Any
    output: Any

class Code(BaseModel):
    source_code: str
    shown_tests: List[Test]
    hidden_tests: Optional[List[Test]]

class RunTest(BaseModel):
    # input: str | List[str | int]
    input: Any

class RunCode(BaseModel):
    source_code: str
    tests: List[RunTest]
