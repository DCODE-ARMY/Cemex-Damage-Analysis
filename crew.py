from crewai_tools import  SerperDevTool, DirectoryReadTool
from crewai import Crew, Process,Agent, Task, LLM
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
import yaml
from crewai.flow.flow import Flow, listen, start
from dotenv import load_dotenv
load_dotenv()
import glob
# from PDFQATool import PDFQATool
from vertex_rag_tool import VertexRAGTool
from VisionTool import VisionTool

os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

llm=LLM(model="openai/gpt-4o-mini",temperature=0.4)

with open(".\\agents.yaml",'r') as agents_file:
    agents = yaml.safe_load(agents_file)

with open(".\\tasks.yaml",'r') as tasks_file:
    tasks = yaml.safe_load(tasks_file)

# import mlflow

# mlflow.crewai.autolog()

# # Optional: Set a tracking URI and an experiment name if you have a tracking server
# mlflow.set_tracking_uri("http://localhost:5000")
# mlflow.set_experiment("Cemex")

class CemexCrew:
    def  __init__(self):
        self.rag_tool = VertexRAGTool()
        self.serper_tool = SerperDevTool()
        self.agents = agents
        self.tasks = tasks
        self.vision_tool = VisionTool()
        self.search_directory_tool = DirectoryReadTool('D:\\cemex\\rag_docs')

    # damge diagonstic expert agent
    def damage_diagnostic_expert_agent(self) -> Agent :
        return Agent(config=self.agents['damage_diagnostic_expert'],
                      llm=llm,
                      verbose=True,
                      allow_delegation=False,
                      max_iter=1,
                      multimodal=False,
                      memory=False)
    
    # report writer for image uploaded
    def repair_solution_specialist_agent(self) -> Agent:
        return Agent(config=self.agents['repair_solution_specialist'],
                      tools=[ self.serper_tool],
                      llm=llm,
                      verbose=True,
                      allow_delegation=False,
                      memory=False)
    


    def repair_guide_writer_agent(self) -> Agent:
        return Agent(config=self.agents['repair_guide_writer'],
                      tools=[ self.serper_tool],
                      llm=llm,
                      verbose=True,
                      allow_delegation=False,
                      memory=False)
    
    #analyze image if uploaded
    def structural_identification_task(self) -> Task:
        return Task(config=self.tasks['structural_identification_task'],
                    agent=self.damage_diagnostic_expert_agent(),
                    tools=[ self.vision_tool],
                    )
    # analyze the damage in the image uploaded
    def damage_diagnosis_task(self) -> Task:
        return Task(config=self.tasks['damage_diagnosis_task'],
                    agent=self.damage_diagnostic_expert_agent(),
                    tools=[ self.vision_tool ]
                    # context=[self.structural_identification_task()]
                    )
    


    # retrieve solution based on the context of the damage analysis
    def solution_retrieval_task(self) -> Task:
        return Task(config=self.tasks['solution_retrieval_task'],
                    agent=self.repair_solution_specialist_agent(),
                    
                    tools=[ self.serper_tool,self.rag_tool,self.search_directory_tool ],
                    context=[self.structural_identification_task(),self.damage_diagnosis_task()],)
    
    # only for text query
    def solution_retrieval_task_query(self) -> Task:
        return Task(config=self.tasks['solution_retrieval_task_query'],
                    agent=self.repair_solution_specialist_agent(),
                    llm=llm,
                    tools=[ self.serper_tool,self.rag_tool,self.search_directory_tool ],
                    memory=False)
    
    
    # report writer for image uploaded
    def generate_repair_guide_task_image(self) -> Task:
        return Task(config=self.tasks['generate_repair_guide'],
                    agent=self.repair_guide_writer_agent(),
                    context=[self.structural_identification_task(),self.damage_diagnosis_task(),self.solution_retrieval_task()],
                    tools=[ self.serper_tool,self.rag_tool,self.search_directory_tool ],
                    )
    
    # report writer for no image uploaded
    def generate_repair_guide_task_query(self) -> Task:
        return Task(config=self.tasks['generate_repair_guide']  ,
                    agent=self.repair_guide_writer_agent(),
                    context=[self.solution_retrieval_task_query()],
                    tools=[ self.serper_tool,self.rag_tool,self.search_directory_tool ],
                    )
    
    def get_crew(self,image_uploaded) -> Crew:
        if image_uploaded:
            return Crew(
            agents=[self.damage_diagnostic_expert_agent(),self.repair_solution_specialist_agent(),],#self.repair_guide_writer_agent()
            tasks=[self.structural_identification_task(),self.damage_diagnosis_task(),self.solution_retrieval_task(), ],#self.generate_repair_guide_task_image()
            process= Process.sequential,
            verbose=True,
            memory= False,
            manager_llm= llm,
            
        )
        else:
            return Crew(
                agents=[self.repair_solution_specialist_agent()],#, self.repair_guide_writer_agent()
                tasks=[self.solution_retrieval_task_query(), ],#self.generate_repair_guide_task_query()
                process= Process.sequential,
                verbose=True,
                memory=False
            ) 




        