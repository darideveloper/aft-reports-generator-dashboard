import numpy as np


class SurveyCalcs:

    def __init__(
        self,
        participant: object,
        survey: object,
        report: object,
    ):
        # Save data
        self.participant = participant
        self.survey = survey
        self.company = participant.company
        self.report = report

        # Calculate totals
        self.__save_report_question_group_totals()

    def __get_question_group_total(
        self, question_group: object, participant: object
    ) -> float:
        """Get participant total in specific question group, based on answers

        Args:
            question_group: QuestionGroup object
            participant: Participant object

        Returns:
            float: Total
        """

        # Local import to avoid circular import
        from survey.models import Answer, QuestionOption

        # Return points of answers
        options = QuestionOption.objects.filter(
            question__question_group=question_group,
        )
        answers = Answer.objects.filter(
            question_option__question__question_group=question_group,
            participant=participant,
        )
        
        user_points = sum(answer.question_option.points for answer in answers)
        total_points = sum(option.points for option in options)
        if total_points == 0:
            return 0

        return int(user_points / total_points * 100 * 100) / 100

    def __save_report_question_group_totals(self):
        """Calculate and save totals for the current report"""

        # Local import to avoid circular import
        from survey.models import ReportQuestionGroupTotal, QuestionGroup

        # Get question groups of current survey
        question_groups = QuestionGroup.objects.filter(survey=self.survey).order_by(
            "survey_index"
        )

        # Calculate totals for each question group
        for question_group in question_groups:
            total = self.__get_question_group_total(question_group, self.participant)
            # input(total)

            report_question_group_total, _ = (
                ReportQuestionGroupTotal.objects.get_or_create(
                    report=self.report,
                    question_group=question_group,
                )
            )
            report_question_group_total.total = total
            report_question_group_total.save()

    def get_participant_total(self) -> float:
        """Get the total for the current participant"""

        # Local import to avoid circular import
        from survey.models import ReportQuestionGroupTotal

        # Calculate percentage of total in each question group
        question_groups_total = ReportQuestionGroupTotal.objects.filter(
            report=self.report,
        )

        return 0

    def get_company_totals(self) -> np.ndarray:
        """
        DUMMY FUNCTION
        Get the total number of participants for each company in a survey.

        Args:
            survey: Survey object
            company: Company object

        Returns:
            np.ndarray: Array of totals
        """
        # participants = models.Participant.objects.filter(
        #     company=self.company,
        #     survey=self.survey,
        # )

        # totals = np.array([participant.total for participant in participants])

        # return totals

        return np.array(
            [
                85.1,
                90.2,
                80.3,
                85.4,
                90.5,
                85.6,
                90.7,
                85.8,
                90.9,
                85.0,
                90.1,
                60.2,
                70.3,
                80.4,
                90.5,
                85.6,
                90.7,
                85.8,
                90.9,
                85.0,
            ]
        )

    def get_resulting_paragraphs(self) -> list[dict]:
        """
        DUMMY FUNCTION
        Get the resulting paragraphs for a participant in a survey.

        Args:
            participant: Participant object
            survey: Survey object

        Returns:
            list[dict]: List of dictionaries with the resulting paragraphs
                {
                    "score": int,
                    "text": str,
                }
        """

        return [
            {
                "score": 90,
                "text": "Tu evaluación refleja un conocimiento sólido y avanzado sobre los aspectos clave de la alfabetización tecnológica, lo cual es una fortaleza significativa en tu perfil profesional. Comprendes bien las implicaciones y aplicaciones de tecnologías, lo que te permite tomar decisiones informadas y estratégicas en tu organización. No obstante, es recomendable que sigas profundizando en áreas emergentes, como la automatización de procesos y la cadena de bloques, para mantenerte a la vanguardia de las innovaciones tecnológicas. También podrías centrarte en expandir tu capacidad para fomentar una cultura digital dentro de tu equipo, asegurando que todos estén alineados con las nuevas herramientas y tecnologías. Si continúas desarrollando tus habilidades en la gestión de riesgos tecnológicos y el cumplimiento de normativas globales de seguridad, podrás fortalecer aún más tu liderazgo digital y asegurar que tu organización se mantenga competitiva a largo plazo.",
            },
            {
                "score": 90,
                "text": "Tu evaluación refleja un sólido conocimiento de la línea de tiempo en la evolución tecnológica y su impacto en la vida humana, lo que te posiciona bien para tomar decisiones estratégicas en un entorno altamente digitalizado. Para seguir avanzando, te sugiero que profundices en el impacto de la inteligencia artificial y la automatización en sectores específicos, como la atención médica, servicios y la manufactura o los que podrían aplicarse a tu organización. Estar al tanto de las últimas tendencias en IA te permitirá liderar la integración de estas tecnologías en tu organización para mejorar la productividad y la innovación. Además, sería beneficioso que investigaras más sobre las implicaciones éticas y sociales de la IA, especialmente en relación con la automatización del trabajo. De esta forma, podrás guiar a tu equipo y a tu organización hacia una adopción tecnológica sostenible, anticipando los desafíos del futuro del trabajo.",
            },
            {
                "score": 90,
                "text": "Tu evaluación refleja una sólida comprensión de la diferencia entre Internet y la World Wide Web (WWW), lo que te permite adoptar un enfoque estratégico más integral en la transformación digital y en las inversiones tecnológicas, súmate a los líderes que promueven este progreso. Tienes claro que la infraestructura de Internet va más allá de la WWW e incluye tecnologías como la computación en la nube, la IoT (internet de las cosas) y la cadena de bloques. Para seguir avanzando, te sugiero que continúes profundizando en el impacto de estas tecnologías emergentes, como la computación perimetral (edge computing) y la Internet industrial de las cosas (IIoT), que están remodelando el panorama digital. Al seguir desarrollando tu visión holística de cómo estas tecnologías interrelacionadas afectan la competitividad empresarial, podrás liderar de manera más efectiva la innovación, la protección de datos y las estrategias de crecimiento sostenible dentro de tu organización. ",
            },
            {
                "score": 90,
                "text": "Tu evaluación refleja una sólida comprensión de los dispositivos digitales y sus aplicaciones, lo cual es una fortaleza clave en tu desempeño como líder. Seguramente utilizas herramientas de análisis de datos, colaboración en la nube y automatización de tareas de manera efectiva para optimizar tu tiempo y mejorar la productividad. Sin embargo, para continuar avanzando, te sugiero profundizar en el uso de aplicaciones avanzadas de IA, como asistentes virtuales personalizados o herramientas de análisis predictivo, que pueden ofrecerte nuevas formas de anticipar problemas y tomar decisiones más estratégicas. También es importante que compartas tus conocimientos con tu equipo, fomentando una cultura de adopción tecnológica y asegurándote de que todos estén alineados en el uso de estas herramientas. Esto fortalecerá aún más tu capacidad de liderazgo y tu impacto en la organización.",
            },
            {
                "score": 90,
                "text": "Tu evaluación indica que tienes una comprensión avanzada de la ciberseguridad y de su impacto en la estrategia organizacional, lo que te posiciona como un líder capaz de tomar decisiones clave para proteger los activos digitales de la empresa. Dominas conceptos clave como la gestión de riesgos, la protección de datos y el cumplimiento normativo, y has integrado estas prácticas en las operaciones de la organización. Para seguir avanzando, te recomendaría que lideres iniciativas de concientización sobre ciberseguridad dentro de tu equipo y entorno laboral, asegurándote de que todos, desde los empleados hasta los altos ejecutivos, comprendan la importancia de una cultura de seguridad. También sería valioso que continúes evaluando y mejorando los planes de respuesta a incidentes de la empresa, apoya a los que lideran las áreas de tecnología en todo lo que soliciten, e impulsa las simulaciones regulares para asegurar una respuesta rápida ante cualquier brecha.",
            },
            {
                "score": 90,
                "text": "Tu evaluación refleja una comprensión avanzada sobre la huella digital, lo que te coloca en una posición fuerte como líder en la protección de los activos digitales de la organización. Dominas las estrategias clave, como el uso de contraseñas seguras, la encriptación de datos y la implementación de políticas de acceso controlado, lo cual es esencial para minimizar los riesgos. Para seguir avanzando, te sugiero que continúes investigando las últimas tendencias en ciberseguridad. Además, lidera iniciativas educativas dentro de la organización, capacitando a tu equipo sobre los riesgos de la huella digital y las mejores prácticas de seguridad. Fomentar una cultura de ciberseguridad contribuirá a fortalecer aún más la protección de la organización y minimizará las vulnerabilidades humanas. Mantente también al tanto de las regulaciones de privacidad y seguridad, asegurando que tu empresa cumpla con los estándares internacionales.",
            },
            {
                "score": 90,
                "text": "Tu evaluación refleja una comprensión avanzada y un enfoque ejemplar sobre el uso responsable de la tecnología. Estás bien posicionado para liderar con ética en el ámbito digital, lo que es fundamental para fomentar una cultura de integridad y respeto en tu organización. Has demostrado un compromiso con la transparencia, la privacidad y la creación de un ambiente digital seguro, lo cual es crucial para generar confianza tanto interna como externamente. Para seguir avanzando, te sugiero que sigas promoviendo la educación continua sobre el comportamiento ético en el uso de la tecnología dentro de tu equipo, asegurándote de que todos comprendan su responsabilidad digital. Además, sería valioso que lideres más iniciativas sobre los beneficios y riesgos de las tecnologías emergentes, como la IA y el análisis de datos, y cómo estas pueden implementarse de manera ética en la organización. ",
            },
            {
                "score": 90,
                "text": "Tu evaluación refleja una comprensión avanzada de las herramientas de colaboración en línea y su aplicación en un entorno de trabajo híbrido o remoto. Ya dominas las características clave de plataformas más comunes y eres capaz de utilizarlas para mejorar la eficiencia operativa y el rendimiento de tu equipo. Sin embargo, te sugiero que sigas explorando nuevas formas de integrar estas plataformas con otros sistemas de la organización, como CRM y ERP, para optimizar aún más los flujos de trabajo y automatizar tareas repetitivas. Te recomiendo que lideres la implementación de una estrategia de datos en tu organización. También sería beneficioso que continúes desarrollando tus habilidades en la gestión de equipos distribuidos, asegurando que el trabajo remoto e híbrido se gestione de manera eficiente y cohesionada. Siguiendo estos pasos, continuarás destacándote como un líder adaptado a las tendencias digitales y preparado para afrontar los retos futuros.",
            },
            {
                "score": 90,
                "text": "Tu evaluación refleja un sólido conocimiento y comprensión de las tecnologías emergentes, como la inteligencia artificial, Realidad Virtual (RV) y la cadena de bloques, lo que te coloca en una posición destacada, podrías ser líder digital fuera del área de tecnología. Dominas los conceptos clave y estás bien informado sobre cómo estas tecnologías pueden impactar tu industria y mejorar las operaciones. Para seguir avanzando, te sugiero que te enfoques en implementar la IA de manera más estratégica dentro de tu organización, para mejorar la productividad y la toma de decisiones. Además, dado tu conocimiento sobre la cadena de bloques, podrías explorar formas de integrar contratos inteligentes y otras aplicaciones descentralizadas para optimizar los procesos y aumentar la transparencia en las operaciones de la empresa. También sería valioso que lideres iniciativas educativas ayudando a tu equipo a comprender cómo estas tecnologías pueden mejorar su trabajo. ",
            },
            {
                "score": 90,
                "text": "Tu evaluación refleja un conocimiento avanzado de las tecnologías de asistencia y su papel en la creación de una sociedad más inclusiva. Tienes una comprensión sólida de cómo estas herramientas, como los asistentes de voz, los lectores de pantalla y los dispositivos domésticos inteligentes, benefician a las personas con capacidades diferentes, facilitando su independencia y participación en la sociedad. Para seguir avanzando, te sugiero que tomes un enfoque proactivo en la implementación de estas tecnologías dentro de tu organización, garantizando que todos los empleados, independientemente de sus capacidades, tengan acceso a herramientas que mejoren su productividad y bienestar. Además, sería beneficioso que lideres iniciativas para aumentar la conciencia sobre la importancia de la accesibilidad digital y cómo se pueden integrar soluciones de tecnología de asistencia en la vida cotidiana de manera efectiva. ",
            },
            {
                "score": 90,
                "text": "Tu evaluación refleja una comprensión avanzada de los desafíos y oportunidades que presentan las redes sociales para los líderes en la era digital. Tus respuestas sugieren que manejas bien tu presencia en línea, lo que te permite influir positivamente en tu equipo, mejorar la percepción pública de la empresa y generar relaciones de confianza con clientes y socios. No obstante, te recomiendo que sigas perfeccionando tu enfoque al establecer límites aún más rigurosos en el tiempo que dedicas a las redes sociales, para que puedas concentrarte en las prioridades profesionales y reducir la presión psicológica de la conectividad constante. Además, dado tu conocimiento, sería valioso que lideres iniciativas dentro de tu organización para educar a tu equipo sobre el uso responsable de las plataformas digitales, promoviendo una cultura de bienestar y respeto en línea. Siguiendo estas prácticas, fortalecerás tu influencia como un líder responsable y equilibrado.",
            },
            {
                "score": 90,
                "text": "Tu evaluación refleja un excelente dominio de las prácticas sostenibles relacionadas con la tecnología y el medio ambiente. Tienes una comprensión profunda de cómo la adopción de tecnologías ecológicas, como el uso de energías renovables y el reciclaje de equipos electrónicos, pueden beneficiar tanto al medio ambiente como a la sostenibilidad de la empresa. Te sugiero que tomes la iniciativa para liderar dentro de tu organización, implementando políticas más rigurosas que promuevan la eficiencia energética y la reducción de la huella de carbono. Además, puedes considerar la creación de una estrategia de sostenibilidad más robusta que incluya la optimización de recursos tecnológicos y la integración de soluciones más verdes en todos los aspectos de la operación empresarial. Sigue explorando nuevas tecnologías ecológicas y asegúrate de que tu empresa esté a la vanguardia en cuanto a sostenibilidad digital.",
            },
            {
                "score": 90,
                "text": "Tu evaluación refleja un nivel sobresaliente en cuanto a etiqueta digital, lo que indica que tienes una gran capacidad para comunicarte de manera respetuosa y profesional en plataformas digitales. Sabes manejar diferentes tipos de comunicación y eres consciente de la importancia de la rapidez y la claridad en las respuestas. Además, muestras una excelente habilidad para adaptarte a las expectativas de las diversas generaciones, lo que te permite gestionar equipos de manera efectiva en un entorno digital. Sin embargo, es importante que continúes perfeccionando tu capacidad para respetar los límites digitales, tanto para ti como para tu equipo, especialmente en un entorno remoto donde el trabajo puede fácilmente invadir el tiempo personal. Te sugiero que sigas promoviendo un uso responsable de las tecnologías y sigas modelando un comportamiento digital positivo para tu equipo. No olvides que liderar con el ejemplo es una ventaja única. ",
            },
        ]

    def get_resulting_titles(self) -> dict:
        """
        DUMMY FUNCTION
        Get the resulting titles for a participant in a survey.

        Args:
            participant: Participant object
            survey: Survey object

        Returns:
            dict: Dictionary with the resulting titles
                {
                    "cultura": {
                        "subtitle": str,
                        "paragraph": str,
                    },
                }
        """

        return {
            "cultura": {
                "subtitle": "Líder en adaptación digital",
                "paragraph": "Ha comenzado a incorporar herramientas y conceptos digitales en su práctica diaria, aunque aún depende de apoyo para aplicarlos de forma estratégica. Muestra disposición al aprendizaje, pero necesita mayor consistencia para liderar con seguridad en entornos digitales. Podría hacer un mayor esfuerzo para convertirse en un aliado del área de tecnología en esta era digital.",
            },
            "tecnologia": {
                "subtitle": "Líder digital estratégico",
                "paragraph": "Se mantiene informado sobre tendencias de conectividad y tecnologías emergentes, comprende su impacto en el negocio y las incorpora en discusiones estratégicas. Sabe identificar cuándo una solución digital puede mejorar procesos, hace preguntas relevantes al área técnica y promueve decisiones basadas en datos y oportunidades tecnológicas.",
            },
            "ciberseguridad": {
                "subtitle": "Líder en desarrollo digital responsable",
                "paragraph": "Reconoce la importancia de la ciberseguridad y busca informarse, aunque aún no aplica de forma consistente las buenas prácticas digitales. Muestra disposición a mejorar, participa en iniciativas de concientización y empieza a promover comportamientos responsables en su equipo, aunque requiere acompañamiento para reforzar su rol como referente en este ámbito.",
            },
            "impacto": {
                "subtitle": "Líder en desarrollo de su imagen digital",
                "paragraph": "Es consciente del impacto de su comportamiento en línea y ha comenzado a ajustar sus prácticas, aunque de forma todavía inconsistente. Participa en redes sociales, pero puede tener dificultades para proyectar un mensaje alineado con su rol y valores organizacionales. Requiere fortalecer el criterio y la intención estratégica en su presencia digital.",
            },
            "ambiente": {
                "subtitle": "Líder en transición hacia la sostenibilidad digital",
                "paragraph": "Implementa algunas prácticas sostenibles y comienza a considerar herramientas de asistencia en su entorno laboral. Sin embargo, lo hace de forma aislada o sin una intención clara de integrarlas en su rutina o en la toma de decisiones. Requiere mayor consistencia para alinear sus acciones con una visión digital más integral y una determinación proactiva.",
            },
            "ecosistema": {
                "subtitle": "Líder colaborativo digital",
                "paragraph": "Utiliza con fluidez dispositivos digitales y herramientas colaborativas para coordinar equipos, compartir información y gestionar proyectos en tiempo real. Integra plataformas en la nube, automatiza tareas y promueve una cultura de trabajo ágil, conectada y eficiente. Su ejemplo ayuda a otros a actualizarse y a mantener un ritmo activo.",
            },
        }

    def get_bar_chart_data(self, use_average: bool) -> list[dict]:
        """
        DUMMY FUNCTION
        Get the bar chart data for a participant in a survey.

        Args:
            use_average (bool): Whether to use the average or the specific value

        Returns:
            list[dict]: List of dictionaries with the bar chart data
                {
                    "titulo": str,
                    "valor": int,
                    "promedio": float,
                    "minimo": int,
                    "maximo": int,
                    "descripcion": str,
                    "color": str,
                }
        """
        return [
            {
                "titulo": "Antecedentes tecnológicos",
                "valor": 1,
                "promedio": 6,
                "minimo": 1,
                "maximo": 10,
                "descripcion": "Comprender cómo funcionan las tecnologías y sus efectos sociales fortalece el liderazgo estratégico.",
                "color": "text-tech-red bg-tech-red border-tech-red",
            },
            {
                "titulo": "Evolución tecnológica",
                "valor": 2,
                "promedio": 6,
                "minimo": 1,
                "maximo": 10,
                "descripcion": "Conocer la evolución tecnológica permite anticipar cambios y liderar la innovación.",
                "color": "text-tech-red bg-tech-red border-tech-red",
            },
            {
                "titulo": "Internet y conectividad",
                "valor": 3,
                "promedio": 7,
                "minimo": 1,
                "maximo": 10,
                "descripcion": "Diferenciar Web e Internet ayuda a planear mejor la infraestructura y seguridad digital.",
                "color": "text-tech-red bg-tech-red border-tech-red",
            },
            {
                "titulo": "Dispositivos digitales",
                "valor": 4,
                "promedio": 7.88,
                "minimo": 1,
                "maximo": 10,
                "descripcion": "Usar correctamente dispositivos digitales mejora productividad y colaboración en tiempo real.",
                "color": "text-tech-red bg-tech-red border-tech-red",
            },
            {
                "titulo": "Ciberseguridad",
                "valor": 5,
                "promedio": 6,
                "minimo": 1,
                "maximo": 10,
                "descripcion": "Proteger los datos y gestionar riesgos es clave para mantener la resiliencia organizacional.",
                "color": "text-tech-red bg-tech-red border-tech-red",
            },
            {
                "titulo": "Huella digital",
                "valor": 6,
                "promedio": 7.5,
                "minimo": 1,
                "maximo": 10,
                "descripcion": "Controlar la huella digital protege la privacidad personal y corporativa frente a amenazas.",
                "color": "text-tech-green bg-tech-green border-tech-green",
            },
            {
                "titulo": "Uso de la tecnología",
                "valor": 7,
                "promedio": 8,
                "minimo": 1,
                "maximo": 10,
                "descripcion": "Un liderazgo ético y responsable en lo digital genera confianza y respeto.",
                "color": "text-tech-green bg-tech-green border-tech-green",
            },
            {
                "titulo": "Herramientas de colaboración",
                "valor": 8,
                "promedio": 8,
                "minimo": 1,
                "maximo": 10,
                "descripcion": "Usar bien las herramientas colaborativas mejora flujos de trabajo y eficiencia.",
                "color": "text-tech-green bg-tech-green border-tech-green",
            },
            {
                "titulo": "Tecnologías emergentes",
                "valor": 9,
                "promedio": 9,
                "minimo": 1,
                "maximo": 10,
                "descripcion": "Conocer y aplicar tecnologías emergentes permite innovar y mantenerse competitivo.",
                "color": "text-tech-green bg-tech-green border-tech-green",
            },
            {
                "titulo": "Tecnologías de asistencia",
                "valor": 10,
                "promedio": 5,
                "minimo": 1,
                "maximo": 10,
                "descripcion": "Fomentar su uso promueve la inclusión y la equidad para todos.",
                "color": "text-tech-green bg-tech-green border-tech-green",
            },
            {
                "titulo": "Rol del líder y la tecnología",
                "valor": 10,
                "promedio": 7,
                "minimo": 1,
                "maximo": 10,
                "descripcion": "Gestionar redes sociales de forma consciente protege la imagen y el equipo.",
                "color": "text-tech-blue bg-tech-blue border-tech-blue",
            },
            {
                "titulo": "Tecnología y medio ambiente",
                "valor": 7,
                "promedio": 6,
                "minimo": 1,
                "maximo": 10,
                "descripcion": "Adoptar prácticas sostenibles reduce el impacto ambiental de la tecnología.",
                "color": "text-tech-blue bg-tech-blue border-tech-blue",
            },
            {
                "titulo": "Etiqueta digital",
                "valor": 7,
                "promedio": 8,
                "minimo": 1,
                "maximo": 10,
                "descripcion": "Mantener una comunicación respetuosa en línea mejora relaciones y confianza.",
                "color": "text-tech-blue bg-tech-blue border-tech-blue",
            },
        ]
