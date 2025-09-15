from crewai import Agent, Crew, Task
from sqlalchemy.orm import Session

from app.models.processed_data import ProcessedData
from app.models.user import User
from app.utils.generic_controller import GenericController
from app.utils.llm import get_llm


class DataProcessingController(GenericController):
    def __init__(self):
        super().__init__(ProcessedData)

    def process_and_persist(
        self,
        db_session: Session,
        input_text: str,
        user: User,
        user_ip: str,
    ) -> ProcessedData:
        llm = get_llm()
        analyst_agent = Agent(
            role='Analista de Dados',
            goal='Processar dados com IA',
            backstory='Expert em análise com IA.',
            llm=llm,
            verbose=True,
        )
        task = Task(
            description=f'Processar: {input_text}',
            agent=analyst_agent,
            expected_output='Resultado processado.',
        )
        crew = Crew(agents=[analyst_agent], tasks=[task], verbose=True)
        result = crew.kickoff()

        processed = ProcessedData(
            input_text=input_text,
            processed_result=result.raw,
            user=user,
            audit_user_ip=user_ip,
            audit_user_login=user.username,
        )
        return super().save(db_session, processed)
