import os
import json
import time
import toml
import datetime
import streamlit as st
import pandas as pd
import streamlit_antd_components as sac


path = os.path.abspath(os.path.dirname(__file__))
with open(f'{path}/config/style.json', 'r', encoding="utf-8") as file:
    style_data = json.load(file)
with open(f'{path}/config/api.toml', 'r', encoding="utf-8") as json_file:
    config = toml.load(json_file)
with open(f'{path}/config/url.json', 'r', encoding="utf-8") as json_file:
    url_data = json.load(json_file)


def json_input_flow1(p, g, a, positive_prompt, negative_prompt):
    data = {
        "user_prompts": [p],
        "gpt": {
            "gpt_prompt": config["gpt"]["prompt"]
        },
        "user": {
            "gender": g,
            "ages": a
        },
        "template": {
            "prompt": positive_prompt,
            "negative_prompt": negative_prompt
        }
    }
    return data


def json_input_flow2(p, g, a, s):
    data = {
        "user_prompts": [p],
        "gpt": {
            "gpt_prompt": config["gpt"]["prompt"]
        },
        "user": {
            "gender": g,
            "ages": a
        },
        "template": {
            "prompt": style_data[s]["positive"],
            "negative_prompt": style_data[s]["negative"]
        }
    }
    return data


def get_url(data):  # 发送json数据，返回json数据

    # response = {
    #    'chat_result': chat_result,
    #    'image_url': oss_image_url,
    #    'chat_time': time1,
    #    'sd_time': time2,
    #    'total_time': time3
    # }

    return response


st.set_page_config(page_title='Prompt Test', page_icon=':shark:', layout='wide', initial_sidebar_state='expanded')


with st.sidebar:
    st.title('Prompt Test')

    sac.divider("测试设置", align="center", color="gray")
    key = st.text_input('密钥:', placeholder='输入密钥后使用')
    num = st.number_input('每次生成图片的数量:', min_value=1, max_value=5, value=1)

    sac.divider("模拟用户", align="center", color="gray")
    gender = st.selectbox('性别:', ['男', '女'], index=1)
    age = st.selectbox('年龄:', ['18-30', '31-45', '46-59', '60+'], index=0)
    user_prompt = st.text_area('写作:', placeholder='在这里模拟用户写作。如：今天风景真不错啊!', height=200)

if key == "123456":
    choose = sac.segmented(
        items=[
            sac.SegmentedItem(label='调整提示词', icon='file-text'),
            sac.SegmentedItem(label='现有提示词', icon='gear-fill'),
            sac.SegmentedItem(label='所有数据', icon='pc-display'),
        ], align='center', use_container_width=True
    )


    if choose == '调整提示词':

        with st.expander("**预置提示词**", icon=":material/construction:"):
            col1, col2 = st.columns(2)
            with col1:
                if st.checkbox("加载预置提示词"):
                    with col2:
                        style = st.selectbox('选择预置提示词', style_data.keys(), label_visibility="collapsed")

        # 调整提示词
        with st.container(border=True):
            try:
                name = st.text_input('提示词风格命名', style, key="name", placeholder="请命名此组提示词风格")
                col1, col2 = st.columns(2)
                with col1:
                        positive = st.text_area('正向提示词', style_data[style]["positive"], key="positive", height=200, help="在这里输入正向提示词请务必预留 **{prmopt}** 作为用户输入占位符")
                with col2:
                        negative = st.text_area('负向提示词', style_data[style]["negative"], key="negative", height=200, help="在这里输入负向提示词")
            except:
                name = st.text_input('提示词风格命名')
                col1, col2 = st.columns(2)
                with col1:
                        positive = st.text_area('正向提示词', height=200)
                with col2:
                        negative = st.text_area('负向提示词', height=200)

            st.warning("正向提示词请务必预留 **{prmopt}** 作为用户输入占位符；提示词命名相同时，会自动覆盖原有提示词！")

            # 开始测试
            col1, col2, col3 = st.columns([0.2, 0.2, 0.6])
            with col1:
                if st.button('测试效果', use_container_width=True, type="primary"):
                    if user_prompt != "\n" and user_prompt is not None:
                        if "{prmopt}" in positive:
                            with st.spinner('请等待...'):

                                url_flow1 = []
                                for i in range(num):
                                    json_data = json_input_flow1(user_prompt, gender, age, positive, negative)  # 发送的json数据
                                    respond = get_url(json_data)   # 接收的json数据
                                    url_flow1.append(respond["image_url"])  # 保存URL
                                    time.sleep(0.01)
                                    current_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                                    current_time = current_time + f"【{str(i+1)}】"
                                    url_data["flow1"].update({current_time: respond["image_url"]})
                                    with open(f'{path}/config/url.json', 'w', encoding="utf-8") as f:
                                        json.dump(url_data, f, ensure_ascii=False, indent=4)

                                st.session_state.url_flow1 = url_flow1
                        else:
                            st.error("请预留 {prmopt} 作为用户输入占位符！")
                    else:
                        st.error("请填写用户写作！")

            with col2:
                if st.button('保存此组提示词', use_container_width=True, type="primary"):
                    if "{prmopt}" in positive:
                        style_data.update({name: {"positive": positive, "negative": negative}})
                        with open(f'{path}/config/style.json', 'w', encoding="utf-8") as f:
                            json.dump(style_data, f, ensure_ascii=False, indent=4)
                    else:
                        st.error("请预留 {prmopt} 作为用户输入占位符！")

        # 加载图片
        st.write('')
        with st.container(border=True):
            if "url_flow1" in st.session_state:
                col3, col4, col5, col6, col7 = st.columns(5)
                num_images = len(st.session_state.url_flow1)
                for i in range(num_images):
                    if i % 5 == 0:
                        col = col3
                    elif i % 5 == 1:
                        col = col4
                    elif i % 5 == 2:
                        col = col5
                    elif i % 5 == 3:
                        col = col6
                    elif i % 5 == 4:
                        col = col7
                    with col:
                        try:
                            st.image(st.session_state.url_flow1[i])
                        except:
                            st.write("此图片生成失败！")

    if choose == '现有提示词':
        with st.expander("**现有提示词**", expanded=True, icon=":material/construction:"):
            rows = [[key, prompt["positive"], prompt["negative"]] for key, prompt in style_data.items()]
            datas = pd.DataFrame(rows, columns=["提示词名称", "正向提示词", "负向提示词"])
            datas = st.data_editor(datas, num_rows="dynamic", height=248)
            col3, col4, col5, col6, col7 = st.columns(5)
            with col3:
                if st.button('保存修改', use_container_width=True, type="primary"):
                    style_data = {row[0]: {"positive": row[1], "negative": row[2]} for row in datas.values}
                    with open(f'{path}/config/style.json', 'w', encoding="utf-8") as f:
                        json.dump(style_data, f, ensure_ascii=False, indent=4)

        with st.container(border=True):
            style = st.selectbox('选择测试风格', style_data.keys())
            col3, col4, col5, col6, col7 = st.columns(5)
            with col3:
                if st.button('测试效果', use_container_width=True, type="primary"):
                    if user_prompt != "\n" and user_prompt is not None:
                        with st.spinner('请等待...'):

                            url_flow2 = []
                            for i in range(num):
                                json_data = json_input_flow2(user_prompt, gender, age, style)  # 发送的json数据
                                respond = get_url(json_data)  # 接收的json数据
                                url_flow2.append(respond["image_url"])  # 保存URL
                                time.sleep(0.01)
                                current_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                                current_time = current_time + f"【{str(i+1)}】"
                                url_data["flow2"].update({current_time: respond["image_url"]})
                                with open(f'{path}/config/url.json', 'w', encoding="utf-8") as f:
                                    json.dump(url_data, f, ensure_ascii=False, indent=4)

                            st.session_state.url_flow2 = url_flow2
                    else:
                        st.error("请填写用户写作！")

        # 加载图片
        with st.container(border=True):
            if "url_flow2" in st.session_state:
                col3, col4, col5, col6, col7 = st.columns(5)
                num_images = len(st.session_state.url_flow2)
                for i in range(num_images):
                    if i % 5 == 0:
                        col = col3
                    elif i % 5 == 1:
                        col = col4
                    elif i % 5 == 2:
                        col = col5
                    elif i % 5 == 3:
                        col = col6
                    elif i % 5 == 4:
                        col = col7
                    with col:
                        try:
                            st.image(st.session_state.url_flow2[i])
                        except:
                            st.write("此图片生成失败！")

    if choose == '所有数据':
        flow = st.selectbox('选择要查看的测试数据', ['工作流1 - 调整提示词', '工作流2 - 现有提示词'])
        if flow == '工作流1 - 调整提示词':
            row_flow1 = [[key, url] for key, url in url_data["flow1"].items()]
            row_flow1 = sorted(row_flow1, key=lambda x: x[0], reverse=True)
            data_flow1 = pd.DataFrame(row_flow1, columns=["时间", "URL"])
            st.dataframe(data_flow1, use_container_width=True, hide_index=True)

        if flow == '工作流2 - 现有提示词':
            row_flow2 = [[key, url] for key, url in url_data["flow2"].items()]
            row_flow2 = sorted(row_flow2, key=lambda x: x[0], reverse=True)
            data_flow2 = pd.DataFrame(row_flow2, columns=["时间", "URL"])
            st.dataframe(data_flow2, use_container_width=True, hide_index=True)

        st.info("由于后期数据太多，请自行复制链接查看！")
else:
    st.error("在左侧填写密钥后使用！")