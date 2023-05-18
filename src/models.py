from typing import List
from pydantic import BaseModel

class Test(BaseModel):
    input: str
    output: str

class Code(BaseModel):
    source_code: str
    shown_tests: List[Test]
    hidden_tests: List[Test]

class RunTest(BaseModel):
    input: str

class RunCode(BaseModel):
    source_code: str
    tests: List[RunTest]
