[English](README.md) | [한국어](README.ko.md) | [中文](README.zh.md) | [日本語](README.ja.md) | Español

# vibe-sunsang (바선생)

<p align="center">
  <img src="assets/vibe-sunsang-hero-01.png" alt="vibe-sunsang" width="320">
</p>

> **Un agente mentor de IA que convierte tu historial de conversaciones de Claude Code en un motor de crecimiento.**

vibe-sunsang recopila, convierte y analiza automáticamente cada conversación que tienes con Claude Code, para que con el tiempo te conviertas en un colaborador de IA más eficaz.

[Inicio rápido](#inicio-rápido) • [¿Por qué vibe-sunsang?](#por-qué-vibe-sunsang) • [Cómo funciona](#cómo-funciona) • [Modos](#modos) • [Sistema de niveles](#sistema-de-niveles) • [Requisitos](#requisitos)

---

## Inicio rápido

### 1. Instalación

```
/plugin marketplace add https://github.com/fivetaku/gptaku_plugins.git
/plugin install vibe-sunsang
```

Después, **reinicia Claude Code**.

### 2. Ejecuta el onboarding

En cualquier proyecto:

```
/vibe-sunsang 시작
```

El onboarding hará lo siguiente:

1. Crear el espacio de trabajo `~/vibe-sunsang/` (con `CLAUDE.md`, `.gitignore` y `git init`)
2. Escanear tu historial de conversaciones de Claude Code en `~/.claude/projects/`
3. Dejarte asignar nombres legibles a cada proyecto detectado
4. Clasificar cada proyecto por tipo de espacio de trabajo (Builder / Explorer / Designer / Operator)
5. Convertir todos los registros JSONL a Markdown por primera vez
6. Preguntarte si quieres pasar directamente a la mentoría o a un informe de crecimiento

### 3. Úsalo cada semana

```
/vibe-sunsang 변환      ← convert this week's conversations
/vibe-sunsang 멘토링    ← get coaching on your AI usage patterns
/vibe-sunsang 성장      ← generate a growth report
/vibe-sunsang 지식      ← explore the level system and concepts
```

---

## ¿Por qué vibe-sunsang?

- **Tus conversaciones ya contienen los datos** —Claude Code guarda cada sesión como JSONL. vibe-sunsang lee esos archivos, así que no hay que registrar nada nuevo
- **No solo "qué construí", sino "cómo lo construí"** —el análisis se centra en la calidad de tus peticiones, tus hábitos de recuperación ante errores y tu pensamiento estratégico, no solo en el volumen de resultados
- **Consciente del tipo de espacio de trabajo** —el sistema de niveles se adapta a lo que realmente haces (programar, investigar, planificar o automatizar)
- **Seis dimensiones, no una sola puntuación** —DECOMP, VERIFY, ORCH, FAIL, CTX y META se miden de forma independiente, para que sepas exactamente qué habilidad desarrollar a continuación
- **Seguimiento longitudinal** —cada informe de crecimiento actualiza `TIMELINE.md`, así ves tu progreso a lo largo de meses, no solo de una sesión
- **Apto para no desarrolladores** —coaching en lenguaje llano con analogías, sin muros de jerga técnica

---

## Cómo funciona

```
Claude Code conversation logs (~/.claude/projects/)
                    |
                    | /vibe-sunsang 변환
                    v
     Readable Markdown files (~/vibe-sunsang/conversations/)
                    |
                    | 6-axis analysis
                    | (DECOMP / VERIFY / ORCH / FAIL / CTX / META)
                    v
     Mentoring session  ←→  Growth report  ←→  Concept learning
                    |
                    | Fit Score  ×  workspace-type weights
                    v
     Level judgment: L1.0 – L7.0 (0.5-step increments)
                    |
                    v
     TIMELINE.md (longitudinal growth tracking)
```

Los datos de conversación y el código del plugin viven en directorios separados, así que las actualizaciones del plugin nunca tocan tus datos.

---

## Modos

### Onboarding (`시작`)

Configura el espacio de trabajo `~/vibe-sunsang/`, mapea los nombres de proyecto, clasifica los tipos de espacio de trabajo y ejecuta la primera conversión completa.

---

### Conversión (`변환`)

Convierte los registros JSONL de Claude Code en archivos Markdown legibles, organizados por proyecto.

| Comando | Comportamiento |
|---------|----------------|
| `/vibe-sunsang 변환` | Incremental —solo las sesiones nuevas |
| `/vibe-sunsang 변환 force` | Reconversión completa |
| `/vibe-sunsang 변환 <project name>` | Solo un proyecto |

Cada archivo convertido incluye frontmatter con metadatos: fecha, recuento de tokens, modelo usado y herramientas invocadas. Un `INDEX.md` te da la visión completa de un vistazo.

---

### Mentoría (`멘토링`)

Cuatro modos de coaching, cada uno centrado en dimensiones de habilidad distintas:

| Modo | Disparador | Qué hace | Ejes centrales |
|------|-----------|----------|----------------|
| **A — Calidad de las peticiones** | "요청 코칭해줘" | Califica tus prompts de A a D según claridad y contexto | DECOMP + CTX |
| **B — Diagnóstico de antipatrones** | "뭘 잘못하고 있는지" | Detecta malos hábitos con ejemplos concretos y estrategias de corrección | FAIL + VERIFY |
| **C — Aprendizaje de conceptos** | "이게 뭐야" | Explica en lenguaje llano los conceptos de tus sesiones recientes | META |
| **D — Coaching completo** (por defecto) | "멘토링해줘" | Chequeo completo de los 6 ejes, veredicto de nivel y plan de acción | los 6 ejes |

El modo D genera un gráfico de radar en texto y un plan de acción en tres pasos: una cosa para hacer ahora mismo, una esta semana y una en el plazo de un mes.

Los resultados del coaching pueden guardarse en `~/vibe-sunsang/exports/mentor-YYYY-MM-DD.md`.

---

### Informe de crecimiento (`성장`)

Delega el análisis en un subagente dedicado `growth-analyst` para mantener ligero el contexto principal. El agente lee tus archivos de sesión, puntúa las seis dimensiones y redacta un informe completo.

**Opciones de rango temporal:**

| Rango | Cobertura |
|-------|-----------|
| Esta semana | Últimos 7 días |
| Últimas 2 semanas (recomendado) | Últimos 14 días |
| Este mes | Últimos 30 días |
| Proyecto concreto | Historial completo del proyecto |

**El informe incluye:**

1. Estadísticas básicas —número de sesiones, número de mensajes, uso de tokens
2. Análisis de las 6 dimensiones técnicas con puntuaciones y pesos
3. Gráfico de radar en texto
4. Tabla de estado de las condiciones de puerta (requisitos para alcanzar el siguiente nivel)
5. Detección de antipatrones (calibrada a tu tipo de espacio de trabajo)
6. Comparación longitudinal con todos los informes anteriores
7. Tarjeta de nivel con barra de progreso
8. Mensaje de ascenso si has subido de nivel (L4→L5 tiene un evento especial: "el muro del 80%")
9. Actualización automática de `TIMELINE.md`

---

### Conocimiento (`지식`)

Responde preguntas sobre el propio framework de vibe-sunsang:

| Tema | Descripción |
|------|-------------|
| Sistema de niveles | Progresión de 7 niveles (en incrementos de 0,5) y qué significa cada uno |
| Los seis ejes | Definiciones y ejemplos de DECOMP, VERIFY, ORCH, FAIL, CTX y META |
| Tipos de espacio de trabajo | Qué implica Builder / Explorer / Designer / Operator para tu análisis |
| Antipatrones | Malos hábitos que vigilar, calibrados a tu tipo de espacio de trabajo |
| Calidad de las peticiones | Cómo escribir mejores prompts |
| Métricas de crecimiento | Fórmula del Fit Score, condiciones de puerta, pesos por tipo |

---

## Sistema de niveles

### 6 dimensiones técnicas

| Código | Dimensión | Definición en una línea |
|--------|-----------|-------------------------|
| **DECOMP** | Descomposición de tareas | Dividir peticiones complejas en unidades que la IA puede manejar |
| **VERIFY** | Estrategia de verificación | Revisar críticamente la salida de la IA en lugar de aceptarla sin más |
| **ORCH** | Orquestación | Combinar herramientas, agentes y flujos de trabajo |
| **FAIL** | Recuperación ante fallos | Diagnosticar errores y encontrar alternativas |
| **CTX** | Gestión del contexto | Proporcionar a la IA antecedentes, restricciones y objetivos |
| **META** | Metacognición | Reconocer y ajustar estratégicamente tus patrones de uso de la IA |

### Tipos de espacio de trabajo y pesos

Los pesos del análisis varían según lo que realmente haces:

| Dimensión | Builder | Explorer | Designer | Operator |
|-----------|---------|----------|----------|----------|
| DECOMP | **25%** | 15% | 20% | 15% |
| VERIFY | **25%** | 15% | 15% | 20% |
| ORCH | 15% | 10% | 10% | **25%** |
| FAIL | 15% | **20%** | 10% | **20%** |
| CTX | 10% | **20%** | **25%** | 10% |
| META | 10% | **20%** | **20%** | 10% |

### Progresión de 7 niveles (por tipo de espacio de trabajo)

| Nivel | Builder | Explorer | Designer | Operator |
|-------|---------|----------|----------|----------|
| L1 | Observer | Asker | Dreamer | User |
| L2 | Tinkerer | Curious | Sketcher | Repeater |
| L3 | Collaborator | Digger | Shaper | Optimizer |
| L4 | Pilot | Investigator | Planner | Builder |
| L5 | Architect | Analyst | Strategist | Engineer |
| L6 | Conductor | Synthesizer | Director | Orchestrator |
| L7 | Forgemaster | Scholar | Visionary | Automator |

Los niveles se puntúan internamente con dos decimales y se redondean a incrementos de 0,5 al mostrarse. El criterio no es "¿puedes hacerlo?", sino "¿lo haces de forma consistente?".

### Condiciones de puerta

| Puerta | Requisito |
|--------|-----------|
| L3 | Ratio de especificidad de contexto > 0.5 |
| L4 | Ratio de verificación > 0.15 Y ratio de corrección > 0.05 |
| L5 | Diversidad de herramientas > 8 (o uso de herramienta de orquestación) Y ratio estratégico > 0.05 |
| L6 | Experiencia multiagente demostrada |
| L7 | Puerta de L6 + evidencia de contribución externa |

---

## Rutina sugerida

**Cada viernes (15 min)**

```
1. /vibe-sunsang 변환      ← convert this week's sessions
2. 멘토링해줘               ← weekly review
3. Pick one thing to try next week
```

**Cada mes (30 min)**

```
1. /vibe-sunsang 변환 force  ← full re-convert
2. 성장 리포트 만들어줘        ← monthly growth report
3. Compare with previous reports — trends are shown automatically
```

---

## Estructura de archivos

Todos los datos del usuario viven en `~/vibe-sunsang/`. El código del plugin vive aparte.

```
~/vibe-sunsang/
├── CLAUDE.md                 ← workspace description (created by onboarding)
├── .gitignore
├── config/                   ← project name map, workspace type classifications
├── conversations/            ← converted Markdown sessions
│   └── INDEX.md              ← full project index
├── exports/                  ← growth reports, mentor session saves
└── growth-log/
    ├── TIMELINE.md           ← level and 6-axis history across all reports
    └── weekly/               ← weekly retrospective notes
```

---

## Requisitos

- CLI de [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- Python 3.8+

### Ruta de origen de las conversaciones

Por defecto, vibe-sunsang lee las sesiones desde `~/.claude/projects/`. El orden de resolución:

1. Parámetro `--projects-dir <path>` (pasado a `convert_sessions.py`)
2. `$CLAUDE_CONFIG_DIR/projects` si la variable de entorno `CLAUDE_CONFIG_DIR` está definida
3. `~/.claude/projects/` (por defecto)
4. Alternativa para WSL: `/mnt/c/Users/$USER/.claude/projects` (solo si 1–3 no resuelven)

Usa `--projects-dir` cuando trabajes entre entornos (p. ej., WSL ↔ Windows) o cuando tu configuración de Claude esté fuera de `~/.claude/`:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/convert_sessions.py \
  --projects-dir /custom/path/.claude/projects \
  --output-dir "$HOME/vibe-sunsang/conversations"
```

---

## Licencia

MIT

---

<div align="center">

**Deja de adivinar cómo mejorar. Deja que tus propias conversaciones te lo muestren.**

</div>
