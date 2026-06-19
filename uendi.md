# [cite_start]1. Introducción y Contexto del Proyecto [cite: 1]

## [cite_start]1.1 Resumen ejecutivo [cite: 2]
[cite_start]Este documento presenta una propuesta técnica para evolucionar a Uendi, el chatbot de atención al cliente del Banco Ueno, hacia una arquitectura de Generación Aumentada por Recuperación (Retrieval-Augmented Generation, RAG). [cite: 3]

[cite_start]El objetivo es resolver un problema concreto de negocio — la desactualización del conocimiento del chatbot frente al ritmo de lanzamiento de nuevos productos bancarios — mediante un sistema que permita a Uendi acceder a información actualizada sin necesidad de reentrenar o reconfigurar manualmente el modelo de lenguaje subyacente. [cite: 4]

[cite_start]El documento está organizado en tres niveles de lectura: (1) una base teórica que explica por qué los modelos de lenguaje de gran escala (LLM) requieren un mecanismo como RAG, (2) una propuesta de arquitectura técnica de nivel empresarial, con sus componentes, flujos y stack tecnológico, y (3) un análisis crítico de riesgos, costos y un roadmap realista para llevar el proyecto de prototipo a producción. [cite: 5]

[cite_start]Es importante aclarar el alcance: este es un proyecto académico desarrollado en el marco de un curso de Inteligencia Artificial Generativa, no una implementación comercial contratada por Ueno Bank. [cite: 6] [cite_start]Sin embargo, el diseño se elabora con el mismo nivel de rigor que se aplicaría a un caso real, incluyendo consideraciones de seguridad, cumplimiento normativo y costos propias del sector financiero paraguayo. [cite: 7]

## [cite_start]1.2 El problema de negocio [cite: 8]
[cite_start]Uendi, como muchos chatbots bancarios construidos sobre un LLM con prompts e información "hardcodeada" o cargada manualmente, depende de que un equipo humano actualice su base de conocimiento cada vez que el banco lanza un producto, modifica una tasa, cambia un requisito o publica una nueva promoción. [cite: 9]

[cite_start]Este proceso manual genera una ventana de desactualización (a veces de días o semanas) durante la cual el chatbot puede responder con información incorrecta o, peor, inventar una respuesta plausible pero falsa. [cite: 10] [cite_start]En la industria bancaria, donde la precisión de la información tiene implicancias regulatorias, reputacionales y de confianza del cliente, este problema no es menor. [cite: 11]

[cite_start]Un chatbot que informa mal una tasa de interés, un requisito de un préstamo o una condición de una tarjeta de crédito puede generar reclamos, pérdida de confianza y, en escenarios extremos, exposición legal para el banco. [cite: 12]

## [cite_start]1.3 La solución propuesta en una frase [cite: 13]

| Propuesta central |
| :--- |
| Construir un sistema de gestión de conocimiento basado en RAG donde los empleados del banco suban documentos (PDFs, folletos de productos, términos y condiciones, documentación interna, FAQs) y el sistema automáticamente extraiga el texto, aplique OCR cuando sea necesario, limpie los datos, los divida en fragmentos (chunks), genere embeddings, los almacene en una base de datos vectorial y actualice la base de conocimiento. [cite_start]Uendi consulta esa base en tiempo de respuesta, sin que el LLM necesite ser reentrenado. [cite: 14] |

[cite_start]El resto de este documento desarrolla, justifica y pone a prueba esta propuesta. [cite: 15]

---

# [cite_start]2. Fundamentos Teóricos: Por Qué los LLM Necesitan RAG [cite: 16]

[cite_start]Antes de diseñar cualquier arquitectura, es necesario entender la raíz del problema a nivel arquitectónico. [cite: 17] [cite_start]RAG no es una moda ni una capa decorativa sobre un LLM: es una respuesta directa a limitaciones estructurales del Transformer, la arquitectura sobre la que se construyen GPT, Claude, Gemini y prácticamente todos los LLM modernos. [cite: 18]

## [cite_start]2.1 La ventana de atención limitada [cite: 19]

### [cite_start]2.1.1 ¿Qué es la ventana de contexto? [cite: 20]
[cite_start]Un modelo Transformer no "lee" un texto de la misma forma que una base de datos almacena registros. [cite: 21] [cite_start]Todo lo que el modelo "sabe" en el momento de generar una respuesta se reduce a lo que entra en su ventana de contexto (context window): la secuencia de tokens — fragmentos de palabras — que se le pasa como entrada en una sola llamada. [cite: 22]

[cite_start]Si la ventana de contexto de un modelo es, por ejemplo, de 128.000 tokens, todo el historial de la conversación, el prompt del sistema, los documentos adjuntos y la pregunta del usuario deben competir por ese mismo espacio finito. [cite: 23] [cite_start]Esto tiene una consecuencia directa para un chatbot bancario: el catálogo completo de productos de Ueno Bank, sus términos y condiciones, las preguntas frecuentes y la documentación interna fácilmente suman millones de tokens. [cite: 24] [cite_start]Es físicamente imposible — y económicamente absurdo, por el costo por token — pegar todo ese conocimiento dentro de cada prompt. [cite: 25]

### [cite_start]2.1.2 El mecanismo de atención (self-attention) [cite: 26]
[cite_start]El Transformer procesa una secuencia calculando, para cada token, una ponderación de "atención" sobre todos los demás tokens de la secuencia: esto es lo que le permite entender que en la frase "el cliente solicitó una tarjeta, pero no la recibió", el "la" se refiere a "tarjeta". [cite: 27] [cite_start]El costo computacional de este mecanismo crece de forma cuadrática con la longitud de la secuencia (duplicar el contexto puede multiplicar por cuatro el costo de cómputo de la atención), lo cual es una de las razones técnicas por las que las ventanas de contexto, aunque hoy son mucho más grandes que hace pocos años, siguen siendo finitas y costosas de ampliar. [cite: 28]

### [cite_start]2.1.3 Por qué los Transformers no pueden "recordar" información ilimitada [cite: 29]
[cite_start]A diferencia de una base de datos relacional, el Transformer no tiene una memoria persistente entre llamadas. [cite: 30] [cite_start]Cada vez que Uendi recibe un mensaje, el modelo parte de cero salvo por lo que se le incluya explícitamente en el prompt de esa llamada. [cite: 31] [cite_start]No existe un "disco duro" interno donde el modelo pueda consultar el catálogo actualizado de productos del banco: solo existe lo que cabe en la ventana de contexto de esa interacción puntual. [cite: 32]

### [cite_start]2.1.4 Degradación en conversaciones largas y dilución de contexto [cite: 33]
[cite_start]Incluso cuando la información cabe dentro de la ventana de contexto, la calidad de uso de esa información no es uniforme. [cite: 34] [cite_start]A medida que una conversación se alarga — o que se incluyen documentos extensos en el prompt — el modelo debe repartir su capacidad de atención entre una cantidad creciente de tokens. [cite: 35] [cite_start]Esto produce lo que se conoce como dilución de contexto: información relevante se "diluye" entre contenido irrelevante o redundante, y el modelo tiene más dificultad para identificar qué parte del contexto es la que realmente responde a la pregunta del usuario. [cite: 36]

### [cite_start]2.1.5 El problema "lost in the middle" [cite: 37]
[cite_start]Investigaciones empíricas sobre el comportamiento de los LLM frente a contextos largos muestran un patrón consistente: los modelos recuperan con mayor precisión la información que se encuentra al principio o al final del contexto, y pierden precisión sobre la información ubicada en el medio. [cite: 38] [cite_start]Esto se conoce coloquialmente como el problema "lost in the middle" (perdido en el medio). [cite: 39]

[cite_start]Para Uendi, esto significa que si se intentara resolver el problema de conocimiento simplemente "pegando todo el manual de productos" en cada prompt, el modelo respondería de forma confiable sobre el primer y el último producto de la lista, pero con menor fiabilidad sobre los productos ubicados en posiciones intermedias — un comportamiento inaceptable para un banco, donde todos los productos deben tratarse con la misma fiabilidad. [cite: 40]

### [cite_start]Ejemplo práctico [cite: 41]

| Ejemplo: el problema sin RAG |
| :--- |
| Supongamos que se intenta "arreglar" a Uendi pegando el PDF completo de 80 páginas de términos y condiciones de todas las tarjetas de crédito dentro del prompt del sistema en cada conversación. [cite_start]El resultado: (1) cada llamada al modelo se vuelve mucho más cara y lenta porque se procesan miles de tokens innecesarios para preguntas simples, (2) el modelo puede confundir condiciones de una tarjeta con las de otra si están ubicadas en el medio del documento, y (3) en cuanto el banco lance un producto nuevo, hay que volver a editar manualmente ese PDF y desplegar el cambio — exactamente el problema original que se quería resolver. [cite: 42] |

## [cite_start]2.2 Consecuencias de estas limitaciones [cite: 43]
[cite_start]Las limitaciones arquitectónicas descritas arriba no son abstractas: se traducen en fallas observables y medibles en producción. [cite: 44] 

[cite_start]**Consecuencias de las limitaciones del Transformer en un chatbot bancario:** [cite: 45]

| Consecuencia | Manifestación en Uendi |
| :--- | :--- |
| Pérdida de coherencia | [cite_start]El bot contradice algo que dijo unos mensajes antes en la misma conversación, porque esa parte del contexto perdió peso relativo. [cite: 46] |
| Pérdida de contexto | [cite_start]El bot "olvida" un dato que el cliente proporcionó al inicio de la conversación (ej. el tipo de cuenta) y vuelve a preguntarlo. [cite: 46] |
| Reducción de precisión | [cite_start]Ante documentos largos en el prompt, el bot extrae datos de la sección equivocada (ej. mezcla tasas de un producto con las de otro). [cite: 46] |
| Alucinaciones | [cite_start]Ante una pregunta para la cual no tiene información confiable en el contexto, el modelo genera una respuesta plausible pero inventada, en lugar de admitir que no sabe. [cite: 46] |
| Incapacidad de acceder a información nueva | [cite_start]Un producto lanzado ayer simplemente no existe para el modelo, salvo que alguien lo haya incluido manualmente en el prompt o reentrenado el modelo. [cite: 46] |

## [cite_start]2.3 El problema del conocimiento estático [cite: 47]
[cite_start]Hay una segunda limitación, independiente de la ventana de contexto, igualmente crítica: el conocimiento de un LLM es estático por diseño. [cite: 48]

* [cite_start]Conocimiento congelado en el tiempo [cite: 49]
* [cite_start]Sin acceso a información en tiempo real [cite: 50]
* [cite_start]Sin acceso a las bases de datos ni a la documentación interna del banco [cite: 51]
* [cite_start]Incapacidad de responder con confiabilidad sobre productos recién lanzados [cite: 52]

[cite_start]Reentrenar (o incluso hacer fine-tuning) del modelo cada vez que cambia una tasa o se lanza un producto es una estrategia que no escala: cada ciclo de fine-tuning implica preparar datasets, validar que el modelo no haya empeorado en otras tareas, desplegar una nueva versión y, aun así, seguir sin tener una fuente de verdad verificable y auditable para cada respuesta — algo crítico en un entorno regulado como el bancario. [cite: 53]

[cite_start]Este es precisamente el vacío que RAG viene a llenar. [cite: 54]

---

# [cite_start]3. Introducción a RAG (Retrieval-Augmented Generation) [cite: 55]

## [cite_start]3.1 ¿Qué es RAG? [cite: 56]
[cite_start]RAG (Generación Aumentada por Recuperación) es un patrón de arquitectura en el que, antes de que el LLM genere una respuesta, el sistema recupera (retrieve) automáticamente los fragmentos de información más relevantes desde una base de conocimiento externa, y los inyecta en el prompt como contexto adicional. [cite: 57] 

[cite_start]El LLM ya no responde "de memoria": responde leyendo la evidencia que se le presenta, de forma similar a como un analista humano consultaría un manual antes de responder una consulta de un cliente. [cite: 58]

[cite_start]**Motivación histórica** [cite: 59]
[cite_start]El concepto fue formalizado en 2020 por un equipo de investigación que buscaba combinar modelos de lenguaje paramétricos (el conocimiento "memorizado" en los pesos de la red neuronal) con memoria no paramétrica (un índice externo, explícito y editable de documentos). [cite: 60] [cite_start]La motivación original era académica — mejorar tareas de respuesta a preguntas de dominio abierto — pero la industria adoptó RAG masivamente a partir de 2023, cuando las empresas necesitaron conectar LLM de propósito general con su conocimiento privado sin pagar el costo de un reentrenamiento completo. [cite: 61]

[cite_start]**Por qué RAG se volvió necesario** [cite: 62]
[cite_start]RAG se volvió la solución estándar de la industria porque resuelve simultáneamente los dos problemas descritos en la sección anterior: la ventana de contexto finita (recuperando solo lo relevante, en lugar de "todo") y el conocimiento estático (consultando una base que se actualiza de forma independiente del modelo). [cite: 63]

[cite_start]**Ventajas de RAG frente al fine-tuning para incorporar conocimiento:** [cite: 64]

| Dimensión | RAG | Fine-tuning |
| :--- | :--- | :--- |
| Actualización de conocimiento | Inmediata: se sube un documento y está disponible en minutos. | [cite_start]Lenta: requiere reentrenar, validar y redesplegar el modelo. [cite: 65] |
| Costo de actualizar | Bajo (ingestión de documentos). | [cite_start]Alto (cómputo de entrenamiento, GPUs, validación). [cite: 65] |
| Trazabilidad / citación | Alta: se puede mostrar de qué documento salió cada dato. | [cite_start]Baja: el conocimiento queda "disuelto" en los pesos del modelo, no es auditable. [cite: 65] |
| Riesgo de "olvido catastrófico" | No aplica (el modelo base no cambia). | [cite_start]Existe: ajustar el modelo a un dominio puede degradar su desempeño general. [cite: 65] |
| Qué tipo de conocimiento mejora | Conocimiento factual y dinámico (qué sabe el modelo). | [cite_start]Estilo, formato y comportamiento (cómo responde el modelo). [cite: 65] |
| Cumplimiento normativo | Más simple: se puede demostrar la fuente exacta de cada respuesta. | [cite_start]Más difícil: no hay forma de "borrar" un dato específico ya aprendido. [cite: 65] |

[cite_start]En la práctica, RAG y fine-tuning no son mutuamente excluyentes: muchas arquitecturas maduras combinan un modelo base (eventualmente afinado para adoptar el tono y las políticas de respuesta del banco) con RAG para el conocimiento factual y dinámico. [cite: 66] [cite_start]Pero para el problema específico de Uendi — productos que cambian con frecuencia — RAG es claramente el mecanismo correcto como base de la solución. [cite: 67]

## [cite_start]3.2 Los tres pilares de RAG [cite: 68]
[cite_start]Es útil pensar un sistema RAG como tres etapas secuenciales, cada una con sus propios componentes técnicos y sus propios modos de falla. [cite: 69]

### [cite_start]3.2.1 Retrieval (Recuperación) [cite: 70]
[cite_start]Es la etapa donde, dada la pregunta del usuario, el sistema busca dentro de la base de conocimiento los fragmentos más relevantes para responderla. [cite: 71]

* [cite_start]Embeddings [cite: 72]
* [cite_start]Representación vectorial y búsqueda semántica [cite: 73]
* [cite_start]Similitud de coseno (cosine similarity) [cite: 74]
* [cite_start]Recuperación densa (dense retrieval) [cite: 75]
* [cite_start]Recuperación dispersa (sparse retrieval) [cite: 76]
* [cite_start]Recuperación híbrida (hybrid retrieval) [cite: 77]

| Por qué la calidad de retrieval es el componente más importante de un sistema RAG |
| :--- |
| Si la etapa de recuperación no encuentra el fragmento correcto, ningún LLM — por más avanzado que sea — puede generar la respuesta correcta: simplemente no tiene la información delante. Este principio se resume con la frase "garbage in, garbage out" aplicada a RAG: la calidad de la generación tiene un techo determinado por la calidad de la recuperación. [cite_start]Por eso, en sistemas RAG maduros, la mayor parte del esfuerzo de ingeniería y evaluación se invierte en mejorar retrieval (chunking, embeddings, reranking, búsqueda híbrida) antes que en cambiar de modelo generador. [cite: 78] |

### [cite_start]3.2.2 Augmentation (Aumentación / Construcción de contexto) [cite: 79]
[cite_start]Recuperar los documentos correctos no es suficiente: hay que presentarlos al LLM de forma que pueda usarlos efectivamente. [cite: 80]

* [cite_start]Construcción de contexto [cite: 81]
* [cite_start]Enriquecimiento del prompt (prompt enrichment) [cite: 82]
* [cite_start]Inyección de contexto (context injection) [cite: 83]
* [cite_start]Ranking del contexto [cite: 84]
* [cite_start]Optimización de tokens [cite: 85]

[cite_start]Simplemente "pegar documentos" no es suficiente porque el cómo se presenta el contexto afecta directamente qué tan bien el modelo lo usa: el formato, el orden, la cantidad de ruido y la claridad de las instrucciones determinan si el modelo realmente se apoya en la evidencia o la ignora. [cite: 86]

### [cite_start]3.2.3 Generation (Generación) [cite: 87]
[cite_start]Es la etapa final, donde el LLM produce la respuesta en lenguaje natural a partir de la pregunta y el contexto aumentado. [cite: 88]

* [cite_start]Uso del contexto recuperado [cite: 89]
* [cite_start]Generación fundamentada (grounded generation) [cite: 90]
* [cite_start]Generación de citas [cite: 91]
* [cite_start]Proceso de generación de la respuesta [cite: 92]

[cite_start]La calidad de la generación depende, en última instancia, de la calidad de la recuperación: un LLM de última generación con contexto irrelevante producirá una mala respuesta (en el mejor caso dirá "no sé"; en el peor, alucinará), mientras que incluso un modelo más modesto con el contexto exacto correcto puede producir una respuesta precisa y bien fundamentada. [cite: 93] [cite_start]Esta es la razón por la que, frente a un presupuesto limitado, conviene invertir primero en mejorar retrieval antes que en usar el modelo generador más caro disponible. [cite: 94]

---

# [cite_start]4. El Flujo Completo de RAG [cite: 95]

[cite_start]A nivel conceptual, el flujo de una consulta a través de un sistema RAG puede representarse así: [cite: 96]

```text
[Consulta del usuario]
         |
         v
[Procesamiento de la consulta]   <- normalizacion, deteccion de idioma
         |
         v
[Generacion de embedding]        <- la pregunta se convierte en vector
         |
         v
[Busqueda vectorial]             <- se buscan los fragmentos mas cercanos
         |
         v
[Reranking]                      <- se reordenan/filtran los candidatos
         |
         v
[Aumentacion del contexto]       <- se arma el prompt con el contexto
         |
         v
[Generacion con el LLM]          <- el modelo redacta la respuesta
         |
         v
[Respuesta final al usuario]