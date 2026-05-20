STATUS_CHOICES = [
    ("pending", "⏳ Pendiente"),
    ("processing", "⚡ Procesando"),
    ("completed", "✔ Completado"),
    ("error", "✖ Error"),
]

GENDER_CHOICES = [
    ("m", "Masculino"),
    ("f", "Feminino"),
    ("o", "Otro"),
]

BIRTH_RANGE_CHOICES = [
    ("1946-1964", "1946-1964"),
    ("1965-1980", "1965-1980"),
    ("1981-1996", "1981-1996"),
    ("1997-2012", "1997-2012"),
]

POSITION_CHOICES = [
    ("analista", "Analista"),
    ("asesor", "Asesor"),
    ("auxiliar", "Auxiliar"),
    ("contralor", "Contralor"),
    ("coordinador", "Coordinador"),
    ("director", "Director"),
    ("director_general", "Director General"),
    ("director_general_adjunto", "Director General Adjunto"),
    ("enlace_informacion", "Enlace de Información"),
    ("manager", "Gerente"),
    ("inspector", "Inspector"),
    ("investigador", "Investigador"),
    ("jefe_departamento", "Jefe de Departamento"),
    ("operator", "Operador"),
    ("secretario_ejecutivo", "Secretario Ejecutivo"),
    ("subdirector", "Subdirector"),
    ("subsecretario", "Subsecretario"),
    ("supervisor", "Supervisor"),
    ("vicepresidente", "Vicepresidente"),
    ("other", "Otro"),
]

DEPARTMENT_CHOICES = [
    ("direccion_general", "Dirección General"),
    ("servicios_medicos", "Servicios Médicos"),
    ("prestaciones_sociales_economicas", "Prestaciones Sociales y Económicas"),
    ("administracion", "Administración"),
    ("finanzas", "Finanzas"),
    ("desarrollo_humano", "Desarrollo Humano"),
    ("juridica", "Jurídica"),
    ("comunicacion_social", "Comunicación Social"),
    ("unidad_control_interno", "Unidad Control Interno"),
    ("unidad_atencion_derechohabiente", "Unidad Atención al Derechohabiente"),
    ("oic", "O.I.C."),
]

INFLUENCE_HIGH = "high"
INFLUENCE_MEDIUM = "medium"
INFLUENCE_LOW = "low"

INFLUENCE_LEVELS = [
    (INFLUENCE_HIGH, "Alta Influencia"),
    (INFLUENCE_MEDIUM, "Mediana Influencia"),
    (INFLUENCE_LOW, "Baja Influencia"),
]

POSITION_INFLUENCE_MAP = {
    "subsecretario": INFLUENCE_HIGH,
    "secretario_ejecutivo": INFLUENCE_HIGH,
    "vicepresidente": INFLUENCE_HIGH,
    "contralor": INFLUENCE_HIGH,
    "director": INFLUENCE_HIGH,
    "director_general": INFLUENCE_HIGH,
    "director_general_adjunto": INFLUENCE_HIGH,
    "asesor": INFLUENCE_MEDIUM,
    "coordinador": INFLUENCE_MEDIUM,
    "manager": INFLUENCE_MEDIUM,
    "jefe_departamento": INFLUENCE_MEDIUM,
    "subdirector": INFLUENCE_MEDIUM,
    "supervisor": INFLUENCE_MEDIUM,
    "analista": INFLUENCE_LOW,
    "auxiliar": INFLUENCE_LOW,
    "enlace_informacion": INFLUENCE_LOW,
    "operator": INFLUENCE_LOW,
    "investigador": INFLUENCE_LOW,
    "inspector": INFLUENCE_LOW,
    "other": INFLUENCE_LOW,
}
