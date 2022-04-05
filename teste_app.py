# %% TrendFollowing
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="until2023",
                   page_icon=None,
                   layout='wide',
                   initial_sidebar_state='expanded')

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title('Alterar variáveis')

username = st.sidebar.text_input("Usuário", value="teste")
password = st.sidebar.text_input("Senha", type='password')

if password == 'teste123':  # Se acertou a senha, fazer:
   
    
    def mom_mac(corte, slow, fast, mom_janela, multiplo):
        mom={}
        for janela in [63, 42, 21, 16, 10, 4]:
            df_ibov_ret = (1+df_ibov).cumprod() / (1+df_ibov).cumprod().shift(janela) - 1
            df_ibov_vol = df_ibov.rolling(janela).std()*(janela**0.5)
            mom_atual = df_ibov_ret / df_ibov_vol
            mom_atual[mom_atual>2] = 2
            mom_atual[mom_atual<-2] = -2
            #mom_atual.loc[(mom_atual> -0.2) & (mom_atual<0.2)] = 0
            mom[janela] = mom_atual.rename(columns={'IBOV':'MOM'})
    
        mac = (mom[slow] - mom[fast]) / (mom[slow] - mom[fast]).rolling(slow).std()
        #mac = (mom[fast] - mom[slow]) / (mom[fast] - mom[slow]).rolling(slow).std()    
    
        mac[mac>2] = 2
        mac[mac<-2] = -2
        #mac[(mac> -0.2) & (mac<0.2)] = 0
        mac = mac.rename(columns={'MOM': 'MAC'})
        correl = pd.concat([mom[mom_janela], mac], axis = 1).corr().iloc[1,0]
    
        perf_mom = pd.DataFrame(data = mom[mom_janela].shift(1).values * (df_ibov.values - df_cdi.values) * multiplo,
                                index = mac.index, 
                                columns=['MOM'])
        
        perf_mac = pd.DataFrame(data = mac.shift(1).values * (df_ibov.values - df_cdi.values) * multiplo,
                                index = mac.index,
                                columns=['MAC'])
    
        carteira_mom = (1+perf_mom.iloc[corte:]).cumprod()
        carteira_mom = carteira_mom.rename(columns={'MOM':'mom(' + str(mom_janela)+')'})
        carteira_mac = (1+perf_mac.iloc[corte:]).cumprod()
        carteira_mac = carteira_mac.rename(columns={'MOM':'mac(' + str(slow)+ ' x ' + str(fast) + ')'})
        ibov = (1+df_ibov.iloc[corte:]).cumprod()
        completo_normal = pd.concat([carteira_mom, carteira_mac, ibov], axis = 1)
    
        vol_mom = (perf_mom.rolling(mom_janela).std()*252**0.5)
        vol_mac = (perf_mac.rolling(mom_janela).std()*252**0.5)
        vol_ibov = (df_ibov.rolling(mom_janela).std()*252**0.5)
        return completo_normal, vol_mom, vol_mac, vol_ibov
    
        
    
    df_ibov = pd.read_parquet('df_ibov.parquet')
    df_cdi = pd.read_parquet('df_cdi.parquet')
    
    corte = -4000
    slow = 16
    fast = 10
    mom_janela = 42
    multiplo = 0.6
    corte = st.input("Escolher apenas os últimos X dias")
    mom_janela = st.selectbox("Escolher janela do trend", [63, 42, 21, 16, 10, 4])

    completo_normal, vol_mom, vol_mac, vol_ibov = mom_mac(corte, slow, fast, mom_janela, multiplo)
    st.plotly_chart(px.line(completo_normal))
    vols = pd.concat([vol_mom, vol_mac, vol_ibov], axis = 1)
    st.plotly_chart(px.line(vol))
    
