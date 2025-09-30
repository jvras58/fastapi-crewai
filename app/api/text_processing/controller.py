from crewai import Agent, Crew, Task
from sqlalchemy.orm import Session

from app.models.processed_text import ProcessedText
from app.models.user import User
from app.utils.generic_controller import GenericController
from app.utils.llm import get_llm


class TextProcessingController(GenericController):
    def __init__(self):
        super().__init__(ProcessedText)

    def process_text_and_persist(
        self,
        db_session: Session,
        input_text: str,
        user: User,
        user_ip: str,
    ) -> ProcessedText:
        llm = get_llm()
        text_processor_agent = Agent(
            role='Especialista em Processamento de Texto',
            goal='Analisar e melhorar texto usando técnicas de IA',
            backstory='Sou um especialista em análise textual e processamento de linguagem natural. '
                     'Posso corrigir, resumir, melhorar e transformar textos de acordo com diferentes necessidades.',
            llm=llm,
            verbose=False,  # TODO: verbose pode ser True para depuração
        )
        task = Task(
            description=f'Analise e melhore o seguinte texto, considerando gramática, '
                       f'clareza e estrutura: {input_text}',
            agent=text_processor_agent,
            expected_output='Texto processado e melhorado com justificativa das alterações realizadas.',
        )
        crew = Crew(agents=[text_processor_agent], tasks=[task], verbose=False)  # TODO: verbose pode ser True para depuração
        result = crew.kickoff()

        processed = ProcessedText(
            input_text=input_text,
            processed_result=result.raw,
            user=user,
            audit_user_ip=user_ip,
            audit_user_login=user.username,
        )
        return super().save(db_session, processed)
