# LangGraph Teams & Workflow - Sistema de Colaboração Multi-Agentes

## 📋 Resumo da Pesquisa

O LangGraph oferece capacidades avançadas para criar sistemas multi-agentes que colaboram entre si, permitindo que diferentes agentes se ajudem mutuamente a completar tarefas complexas.

## 🏗️ Arquiteturas Principais

### 1. **Supervisor Pattern**
Um agente supervisor que gerencia e direciona outros agentes especializados.

```python
supervisor_agent = create_react_agent(
    model="openai:gpt-4.1",
    tools=[assign_to_research_agent, assign_to_math_agent],
    prompt=(
        "You are a supervisor managing two agents:\n"
        "- a research agent. Assign research-related tasks to this agent\n"
        "- a math agent. Assign math-related tasks to this agent\n"
        "Assign work to one agent at a time, do not call agents in parallel.\n"
        "Do not do any work yourself."
    ),
    name="supervisor",
)
```

### 2. **Swarm Pattern**
Agentes que se transferem controle dinamicamente entre si.

```python
from langgraph_swarm import create_swarm, create_handoff_tool

transfer_to_hotel_assistant = create_handoff_tool(
    agent_name="hotel_assistant",
    description="Transfer user to the hotel-booking assistant.",
)

flight_assistant = create_react_agent(
    model="anthropic:claude-3-5-sonnet-latest",
    tools=[book_flight, transfer_to_hotel_assistant],
    prompt="You are a flight booking assistant",
    name="flight_assistant"
)

swarm = create_swarm(
    agents=[flight_assistant, hotel_assistant],
    default_active_agent="flight_assistant"
).compile()
```

### 3. **Hierarchical Teams**
Múltiplos times organizados hierarquicamente com supervisores em diferentes níveis.

```python
# Time 1: Document Writing
doc_writer_agent = create_react_agent(
    llm,
    tools=[write_document, edit_document, read_document],
    prompt="You can read, write and edit documents based on note-taker's outlines."
)

# Time 2: Chart Generation
chart_generating_agent = create_react_agent(
    llm,
    tools=[read_document, python_repl_tool]
)

# Supervisor principal
doc_writing_supervisor_node = make_supervisor_node(
    llm, ["doc_writer", "note_taker", "chart_generator"]
)
```

## 🔧 Ferramentas Essenciais

### **Handoff Tools**
Permitem que agentes transfiram controle entre si:

```python
def create_handoff_tool(*, agent_name: str, description: str | None = None):
    name = f"transfer_to_{agent_name}"
    description = description or f"Ask {agent_name} for help."

    @tool(name, description=description)
    def handoff_tool(
        state: Annotated[MessagesState, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
    ) -> Command:
        tool_message = {
            "role": "tool",
            "content": f"Successfully transferred to {agent_name}",
            "name": name,
            "tool_call_id": tool_call_id,
        }
        return Command(
            goto=agent_name,
            update={"messages": state["messages"] + [tool_message]},
            graph=Command.PARENT,
        )
    return handoff_tool
```

### **Task Description Handoff**
Transferência com contexto da tarefa:

```python
def create_task_description_handoff_tool(*, agent_name: str, description: str | None = None):
    @tool(name, description=description)
    def handoff_tool(
        task_description: Annotated[str, "Description of what the next agent should do"],
        state: Annotated[MessagesState, InjectedState],
    ) -> Command:
        task_description_message = {"role": "user", "content": task_description}
        agent_input = {**state, "messages": [task_description_message]}
        return Command(
            goto=[Send(agent_name, agent_input)],
            graph=Command.PARENT,
        )
    return handoff_tool
```

## 🎯 Casos de Uso Identificados

### **1. Equipes de Documentação**
- **Document Writer**: Escreve e edita documentos
- **Note Taker**: Cria esboços e estruturas
- **Chart Generator**: Cria visualizações e gráficos

### **2. Sistema de Viagens**
- **Travel Advisor**: Planejamento geral
- **Flight Assistant**: Reservas de voos
- **Hotel Advisor**: Reservas de hotéis

### **3. Sistema de Pesquisa**
- **Research Agent**: Busca informações
- **Math Agent**: Cálculos e análises
- **Chart Generator**: Visualizações

## 🚀 Aplicação Prática para Vanlu

Com base nessa pesquisa, poderíamos implementar:

### **Equipe de Atendimento ao Cliente Vanlu**

```python
# Agente Principal de Vendas
luciano_agent = create_react_agent(
    model="gpt-4.1-mini",
    tools=[transfer_to_specialist, transfer_to_scheduling],
    prompt="Você é Luciano, vendedor especialista da Vanlu..."
)

# Agente Especialista Técnico
technical_agent = create_react_agent(
    model="gpt-4.1-mini",
    tools=[technical_specs, service_details],
    prompt="Você é especialista técnico em estética automotiva..."
)

# Agente de Agendamento
scheduling_agent = create_react_agent(
    model="gpt-4.1-mini",
    tools=[calendar_availability, booking_system],
    prompt="Você especialista em agendamentos da Vanlu..."
)

# Supervisor
supervisor_agent = create_react_agent(
    model="gpt-4.1-mini",
    tools=[
        create_handoff_tool(agent_name="luciano_agent"),
        create_handoff_tool(agent_name="technical_agent"),
        create_handoff_tool(agent_name="scheduling_agent")
    ],
    prompt="Você supervisiona o atendimento da Vanlu..."
)
```

## 🎯 Benefícios para o Projeto

1. **Especialização**: Cada agente foca em sua especialidade
2. **Escalabilidade**: Fácil adicionar novos agentes especializados
3. **Colaboração**: Agentes se ajudam mutuamente
4. **Eficiência**: Transferência inteligente baseada no contexto
5. **Controle**: Supervisor mantém qualidade e direção

## 📚 Recursos Adicionais

- **LangGraph Swarm**: Para sistemas dinâmicos de transferência
- **Human-in-the-Loop**: Para aprovações manuais quando necessário
- **Memory Systems**: Para manter contexto entre interações
- **LangSmith Integration**: Para monitoramento e debugging

---

**Fonte**: Pesquisa realizada com LangGraph Context7 - Setembro 2024