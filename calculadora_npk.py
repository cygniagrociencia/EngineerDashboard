import streamlit as st
import math

# Configuração da página
st.set_page_config(page_title="Dashboard Destorroador NPK", layout="wide")

st.title("⚙️ Dashboard: Destorroador NPK")
st.markdown("Simulador de dimensionamento mecânico e proteção elétrica.")
st.markdown("---")

# Constantes Físicas do Projeto
RPM_BASE = 3400
EFICIENCIA_REDUTOR = 0.85   # Eficiência mecânica da engrenagem

# ---------------------------------------------------------
# PROPRIEDADES DO MATERIAL (GLOBAL)
# ---------------------------------------------------------
st.sidebar.header("🪨 Propriedades do Material")
ENERGIA_NPK = st.sidebar.slider(
    "Energia Específica de Fratura (J/g)", 
    min_value=1.0, max_value=50.0, value=18.0, step=0.5,
    help="Trabalho necessário para romper o grão. NPK = ~15 a 20 J/g. Milho = ~29 J/g."
)
st.sidebar.markdown("---")

# ---------------------------------------------------------
# SELETOR DE SISTEMA (UM CLIQUE PARA MUDAR TUDO)
# ---------------------------------------------------------
st.sidebar.header("🔄 Modo de Simulação")
modo = st.sidebar.radio(
    "Escolha a interface de cálculo:",
    ["⚙️ 1. Sistema Mecânico (Foco em Potência)", "⚡ 2. Sistema Elétrico (Risco de Queima)"]
)
st.sidebar.markdown("---")

# =========================================================
# INTERFACE 1: SISTEMA MECÂNICO ORIGINAL
# =========================================================
if modo == "⚙️ 1. Sistema Mecânico (Foco em Potência)":
    
    st.sidebar.header("⚡ Parâmetros Elétricos")
    tensao = st.sidebar.slider("Tensão Nominal (Vdc)", min_value=12, max_value=48, value=24, step=12, key="tensao_mec")
    corrente = st.sidebar.slider("Corrente Aplicada (A)", min_value=1.0, max_value=50.0, value=4.0, step=0.5, key="corrente_mec")
    eficiencia_motor = st.sidebar.slider("Eficiência do Motor (%)", min_value=10, max_value=100, value=75, step=5, key="eficiencia_mec")
    
    st.sidebar.header("🎛️ Parâmetros do Moinho")
    # Uso do parâmetro 'key' para evitar conflito de variáveis quando mudar de aba
    reducao = st.sidebar.slider("Relação de Redução Planetária (1:X)", 1, 200, 50, 1, key="red_mec")
    st.sidebar.markdown("**Taxa de Moagem Alvo (g/s)**")
    col_sl, col_in = st.sidebar.columns([2, 1])
    
    # Inicializa a memória da taxa se ela não existir
    if "taxa_memoria" not in st.session_state:
        st.session_state.taxa_memoria = 11.0
        
    with col_sl:
        # O slider atualiza a memória
        taxa_moagem = st.slider("Taxa Slider", 0.1, 50.0, step=0.1, key="taxa_mec", label_visibility="collapsed", on_change=lambda: st.session_state.update({"taxa_memoria": st.session_state.taxa_mec}))
    with col_in:
        # A caixinha de texto também atualiza a mesma memória
        taxa_digitada = st.number_input("Taxa Input", min_value=0.1, max_value=50.0, step=0.1, key="taxa_num", label_visibility="collapsed", on_change=lambda: st.session_state.update({"taxa_mec": st.session_state.taxa_num}))
    
    # Define o valor final lido pelo restante dos cálculos
    taxa_moagem = st.session_state.taxa_mec

    # Cálculos Elétricos base para a Potência
    potencia_eletrica = tensao * corrente
    potencia_util = potencia_eletrica * (eficiencia_motor / 100.0)

    # Cálculos Mecânicos
    potencia_exigida = (taxa_moagem * ENERGIA_NPK) / EFICIENCIA_REDUTOR
    rotacao_final = RPM_BASE / reducao
    torque_disponivel = (potencia_util * EFICIENCIA_REDUTOR) / (rotacao_final * (math.pi / 30))

    # Layout (Cards e Memorial de Cálculo)
    painel_esquerdo, painel_direito = st.columns([1.1, 1], gap="large")

    with painel_esquerdo:
        st.subheader("Análise de Conversão de Energia")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.metric(label="Potência Elétrica Consumida", value=f"{potencia_eletrica:.1f} W", help="Calculado via V x A")
        with col_c2:
            st.metric(label="Potência Útil Entregue ao Eixo", value=f"{potencia_util:.1f} W", help="Descontando o calor do motor")

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Análise de Força Bruta")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Torque Disponível nos Rolos", value=f"{torque_disponivel:.2f} N.m")
        with col2:
            st.metric(label="Rotação Final nos Rolos", value=f"{rotacao_final:.1f} RPM")

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Status de Operação")

        # Lógica de Validação
        if potencia_util >= potencia_exigida:
            st.success(
                f"**✅ SISTEMA OPERANDO LISO**\n\n"
                f"A potência exigida para fraturar o NPK é de **{potencia_exigida:.1f} Watts**, "
                f"o que está dentro da margem de segurança da sua potência útil de **{potencia_util:.1f} Watts**."
            )
        else:
            st.error(
                f"**❌ MOTOR EM ESTOL (TRAVADO)**\n\n"
                f"A potência exigida para fraturar o NPK (**{potencia_exigida:.1f} Watts**) é superior "
                f"à potência útil disponível no eixo (**{potencia_util:.1f} Watts**). O material encavalou."
            )

    with painel_direito:
        st.subheader("📚 Memorial de Cálculo")
        
        st.markdown(
            f"> **Parâmetros Base Assumidos**\n"
            f"> * **Energia Específica ($E_e$):** {ENERGIA_NPK} J/g (Trabalho para cisalhar 1g de material)\n"
            f"> * **Eficiência Mecânica ($\\eta_{{redutor}}$):** {EFICIENCIA_REDUTOR * 100:.0f}% (Atrito interno)\n"
            f"> * **Motor:** {RPM_BASE} RPM na base"
        )
        
        st.info(
            f"**1. Conversão Elétrica ➔ Mecânica**\n"
            f"$$P_{{elétrica}} = V \\cdot I$$\n"
            f"$$P_{{elétrica}} = {tensao} \\cdot {corrente} = {potencia_eletrica:.1f} \\text{{ W}}$$\n\n"
            f"$$P_{{útil}} = P_{{elétrica}} \\cdot \\eta_{{motor}}$$\n"
            f"$$P_{{útil}} = {potencia_eletrica:.1f} \\cdot {eficiencia_motor/100:.2f} = {potencia_util:.1f} \\text{{ W}}$$"
        )
        st.warning(
            f"**2. Demanda do Material (Fratura)**\n"
            f"$$P_{{exigida}} = \\frac{{\\text{{Taxa de Moagem}} \\cdot E_e}}{{\\eta_{{redutor}}}}$$\n"
            f"$$P_{{exigida}} = \\frac{{{taxa_moagem:.1f} \\cdot {ENERGIA_NPK}}}{{{EFICIENCIA_REDUTOR}}} = {potencia_exigida:.1f} \\text{{ W}}$$"
        )
        st.success(
            f"**3. Cinemática e Torque**\n"
            f"$$N_{{final}} = \\frac{{\\text{{RPM Base}}}}{{\\text{{Redução}}}}$$\n"
            f"$$N_{{final}} = \\frac{{{RPM_BASE}}}{{{reducao}}} = {rotacao_final:.1f} \\text{{ RPM}}$$\n\n"
            f"$$T_{{disp}} = \\frac{{P_{{útil}} \\cdot \\eta_{{redutor}}}}{{\\omega_{{final}}}}$$\n"
            f"$$T_{{disp}} = \\frac{{{potencia_util:.1f} \\cdot {EFICIENCIA_REDUTOR}}}{{({rotacao_final:.1f} \\cdot \\frac{{\\pi}}{{30}})}} = {torque_disponivel:.2f} \\text{{ N.m}}$$"
        )

# =========================================================
# INTERFACE 2: SISTEMA ELÉTRICO AVANÇADO
# =========================================================
elif modo == "⚡ 2. Sistema Elétrico (Risco de Queima)":
    
    st.sidebar.header("⚡ Limites do Motor Elétrico")
    tensao = st.sidebar.slider("Tensão Nominal (Vdc)", min_value=12, max_value=48, value=24, step=12)
    corrente_nominal = st.sidebar.slider("Corrente Máxima Suportada (A)", min_value=1.0, max_value=50.0, value=4.0, step=0.5)
    eficiencia_motor = st.sidebar.slider("Eficiência do Motor (%)", min_value=10, max_value=100, value=75, step=5)

    st.sidebar.header("🎛️ Parâmetros do Moinho")
    reducao = st.sidebar.slider("Relação de Redução Planetária (1:X)", 1, 200, 50, 1, key="red_ele")
    taxa_moagem = st.sidebar.slider("Taxa de Moagem Alvo (g/s)", 0.1, 50.0, 11.0, 0.1, key="taxa_ele")

    # 1. Cálculos de Demanda (Da pedra para a tomada)
    potencia_mecanica_exigida = (taxa_moagem * ENERGIA_NPK) / EFICIENCIA_REDUTOR
    potencia_eletrica_exigida = potencia_mecanica_exigida / (eficiencia_motor / 100.0)
    corrente_exigida = potencia_eletrica_exigida / tensao

    # 2. Cálculos de Oferta e Cinemática (Do motor para o eixo)
    potencia_util_disponivel = (tensao * corrente_nominal) * (eficiencia_motor / 100.0)
    rotacao_final = RPM_BASE / reducao
    torque_disponivel = (potencia_util_disponivel * EFICIENCIA_REDUTOR) / (rotacao_final * (math.pi / 30))

    # Layout (Cards e Memorial de Cálculo)
    painel_esquerdo, painel_direito = st.columns([1.1, 1], gap="large")

    with painel_esquerdo:
        st.subheader("Análise de Conversão de Energia")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            potencia_eletrica_consumida = tensao * corrente_nominal
            st.metric(label="Potência Elétrica Consumida", value=f"{potencia_eletrica_consumida:.1f} W", help="Calculado via V x A")
        with col_c2:
            st.metric(label="Potência Útil Entregue ao Eixo", value=f"{potencia_util_disponivel:.1f} W", help="Descontando o calor do motor")

        st.markdown("<br>", unsafe_allow_html=True)
        
        st.subheader("Análise de Demanda de Corrente")
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            delta_corrente = corrente_exigida - corrente_nominal
            st.metric(
                label="Corrente Exigida para Moer", 
                value=f"{corrente_exigida:.1f} A", 
                delta=f"{delta_corrente:.1f} A acima do limite" if delta_corrente > 0 else "Seguro", 
                delta_color="inverse"
            )
        with col_e2:
            st.metric(label="Corrente Máxima (Etiqueta)", value=f"{corrente_nominal:.1f} A")

        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Torque Máximo de Trabalho", value=f"{torque_disponivel:.2f} N.m")
        with col2:
            st.metric(label="Rotação Final nos Rolos", value=f"{rotacao_final:.1f} RPM")

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Integridade do Sistema")

        # Lógica de Diagnóstico Elétrico/Mecânico
        if corrente_exigida > corrente_nominal:
            margem_queima = corrente_nominal * 1.2 
            if corrente_exigida > margem_queima:
                st.error(
                    f"**🔥 RISCO CRÍTICO DE INCÊNDIO (MOTOR QUEIMADO)**\n\n"
                    f"Para não travar os rolos trituradores, o motor tentará sugar **{corrente_exigida:.1f} Amperes** da fonte. "
                    f"Como o enrolamento foi projetado para apenas **{corrente_nominal} A**, o calor derreterá instantaneamente o verniz das bobinas, causando curto-circuito."
                )
            else:
                st.warning(
                    f"**⚠️ SOBRECARGA TÉRMICA SEVERA**\n\n"
                    f"A corrente exigida (**{corrente_exigida:.1f} A**) ultrapassou o limite contínuo (**{corrente_nominal} A**). "
                    f"O equipamento está trabalhando em sobrecarga severa. Risco de degradação térmica."
                )
        else:
            st.success(
                f"**✅ OPERAÇÃO ESTÁVEL E FRIA**\n\n"
                f"A demanda mecânica nos rolos gera um esforço elétrico de apenas **{corrente_exigida:.1f} A**, "
                f"o que está perfeitamente dentro da capacidade contínua de **{corrente_nominal} A**. Operação segura."
            )

    with painel_direito:
        st.subheader("📚 Memorial de Cálculo Inverso")
        
        st.markdown(
            f"> **Parâmetros Base Assumidos**\n"
            f"> * **Energia Específica ($E_e$):** {ENERGIA_NPK} J/g (Resistência mecânica ao esmagamento)\n"
            f"> * **Eficiência Mecânica ($\\eta_{{redutor}}$):** {EFICIENCIA_REDUTOR * 100:.0f}% (Rendimento coroa/sem-fim)\n"
            f"> * **Motor:** {RPM_BASE} RPM na base"
        )

        st.warning(
            f"**1. Demanda Mecânica (Rolos)**\n"
            f"$$P_{{mec\\_exigida}} = \\frac{{\\text{{Taxa de Moagem}} \\cdot E_e}}{{\\eta_{{redutor}}}}$$\n"
            f"$$P_{{mec\\_exigida}} = \\frac{{{taxa_moagem:.1f} \\cdot {ENERGIA_NPK}}}{{{EFICIENCIA_REDUTOR}}} = {potencia_mecanica_exigida:.1f} \\text{{ W}}$$"
        )
        st.error(
            f"**2. Reflexo Elétrico (Tomada)**\n"
            f"$$P_{{ele\\_exigida}} = \\frac{{P_{{mec\\_exigida}}}}{{\\eta_{{motor}}}}$$\n"
            f"$$P_{{ele\\_exigida}} = \\frac{{{potencia_mecanica_exigida:.1f}}}{{{eficiencia_motor/100:.2f}}} = {potencia_eletrica_exigida:.1f} \\text{{ W}}$$\n\n"
            f"$$I_{{exigida}} = \\frac{{P_{{ele\\_exigida}}}}{{V}} = \\frac{{{potencia_eletrica_exigida:.1f}}}{{{tensao}}} = {corrente_exigida:.1f} \\text{{ A}}$$"
        )
        st.info(
            f"**3. Risco de Queima (Lei de Joule)**\n"
            f"O calor é proporcional ao quadrado da corrente ($I^2$).\n\n"
            f"Ao saltar a exigência de **{corrente_nominal:.1f} A** para **{corrente_exigida:.1f} A**, a energia térmica dissipada dentro da carcaça do motor não cresce de forma linear, mas exponencial, derretendo o verniz das bobinas de cobre isolante."
        )

st.markdown("---")
st.caption("Física aplicada: Conservação de Energia (V x A), resistência de materiais e Lei de Joule.")