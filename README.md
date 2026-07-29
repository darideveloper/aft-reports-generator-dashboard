# AFT — Reports Generator Dashboard

Backend administrativo del ecosistema **AFT (Alfabetización Tecnológica)**, desarrollado para **LeadForward Global Solutions**. Plataforma de evaluación de competencias tecnológicas que gestiona encuestas, participantes y genera reportes individuales y grupales en PDF.

## Tech Stack

- **Django 4.2 + DRF** — Framework y API REST
- **PostgreSQL** — Base de datos
- **ReportLab + WeasyPrint** — Reportes PDF individuales y grupales
- **Matplotlib, NumPy, SciPy, Pandas** — Análisis de datos y gráficos
- **Amazon S3 (django-storages + boto3)** — Almacenamiento en la nube
- **Django Jazzmin** — Panel administrativo moderno
- **n8n** — Webhooks para generación asíncrona de reportes
- **Docker + Gunicorn** — Despliegue

## Features

- Encuestas multigrupo con ponderaciones y modificadores JSON
- Gestión de participantes con 20 puestos estandarizados y mapeo de influencia
- Reportes individuales PDF con curvas de campana y texto dinámico
- Reportes grupales PDF con mapas de calor, rankings y perfiles estratégicos
- Sistema de eventos: formularios embedibles, puerta de acceso, calendario, leads
- 8 endpoints REST, 17 models admin, 11 comandos de gestión

## Setup

```bash
cp .env.example .env
# Configurar variables de entorno
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## Contacto

Desarrollado por [Smooth Software Solutions (3S)](https://darideveloper.com)

- 🌐 [darideveloper.com](https://darideveloper.com)
- 💬 [WhatsApp](https://api.whatsapp.com/send?phone=5214493402622)
- 📂 [Ver proyecto en el portafolio](https://darideveloper.com/portafolio/aft)
