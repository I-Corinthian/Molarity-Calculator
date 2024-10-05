import streamlit as st
import pandas as pd


def get_data(Compound_Name):
    data = pd.read_csv("chemical_molarity\chemicals_data.csv")  
    data.set_index('Compound Name', inplace=True) 
    value = data.loc[Compound_Name]
    return (value['Molecular Weight'], value['Molecular Formula'])

def calculate_mass(Compound_Name, volume, concentration):
    data = get_data(Compound_Name)
    weight = float(data[0])
    mass = concentration * volume * weight
    return mass

def convert_volume(volume, unit):
    unit_conversion = {'L': 1, 'mL': 1e-3, 'μL': 1e-6}
    return volume * unit_conversion[unit]

def convert_concentration(concentration, unit):
    unit_conversion = {'M': 1, 'mM': 1e-3, 'μM': 1e-6, 'nM': 1e-9, 'pM': 1e-12, 'fM': 1e-15}
    return concentration * unit_conversion[unit]

if "calc_data" not in st.session_state:
    st.session_state["calc_data"] = []
if "edit_index" not in st.session_state:
    st.session_state["edit_index"] = None

st.sidebar.header("Saved Calculations")
sidebar_width = 300
st.sidebar.markdown(
    f"<style>div.stSidebar {{width: {sidebar_width}px;}}</style>",
    unsafe_allow_html=True
)

for i, calc in enumerate(st.session_state["calc_data"]):
    st.sidebar.write(f"Calculation {i + 1}: {calc['Compound']}")
    
    if st.sidebar.button(f"Edit", key=f"edit_button_{i}"):
        st.session_state['edit_index'] = i
        st.session_state['edit_data'] = calc
    
    # Delete button
    if st.sidebar.button(f"Delete", key=f"delete_button_{i}"):
        del st.session_state["calc_data"][i]
        st.experimental_rerun()  # Rerun the app after deletion to update UI

st.title("Chemical Mass Calculator")

compound_names = pd.read_csv("chemical_molarity\chemicals_data.csv")['Compound Name'].tolist()

if st.session_state['edit_index'] is not None:
    edit_index = st.session_state['edit_index']
    edit_data = st.session_state['edit_data']
    compound_name = st.selectbox("Component Name", options=compound_names, index=compound_names.index(edit_data['Compound']))
    volume = st.number_input("Desired Final Volume", min_value=0.0, value=edit_data['Volume'], format="%.6f")
    volume_unit = st.selectbox("Volume Unit", ['L', 'mL', 'μL'])
    concentration = st.number_input("Desired Concentration", min_value=0.0, value=edit_data['Concentration'], format="%.12f")
    concentration_unit = st.selectbox("Concentration Unit", ['M', 'mM', 'μM', 'nM', 'pM', 'fM'])
else:
    compound_name = st.selectbox("Component Name", options=compound_names)
    volume = st.number_input("Desired Final Volume", min_value=0.0, format="%.6f")
    volume_unit = st.selectbox("Volume Unit", ['L', 'mL', 'μL'])
    concentration = st.number_input("Desired Concentration", min_value=0.0, format="%.12f")
    concentration_unit = st.selectbox("Concentration Unit", ['M', 'mM', 'μM', 'nM', 'pM', 'fM'])


if st.button("Add/Update"):
    if compound_name and volume and concentration:
        volume_in_l = convert_volume(volume, volume_unit)
        concentration_in_m = convert_concentration(concentration, concentration_unit)

        if st.session_state['edit_index'] is not None:
            st.session_state["calc_data"][st.session_state['edit_index']] = {
                'Compound': compound_name,
                'Volume': volume_in_l,
                'Concentration': concentration_in_m
            }
            st.session_state['edit_index'] = None  
            st.success("Calculation updated successfully.")
        else:
            st.session_state["calc_data"].append({
                'Compound': compound_name,
                'Volume': volume_in_l,
                'Concentration': concentration_in_m
            })
            st.success("New calculation added successfully.")
        
        st.rerun() 
    else:
        st.error("Please fill in all fields")

if st.button("Calculate"):
    results = []

    for calc in st.session_state["calc_data"]:
        compound_name = calc['Compound']
        volume_in_l = calc['Volume']
        concentration_in_m = calc['Concentration']
        weight = get_data(compound_name)[0]
        mass = calculate_mass(compound_name, volume_in_l, concentration_in_m)
        results.append([compound_name, weight, volume_in_l, concentration_in_m, mass])

    if results:
        result_df = pd.DataFrame(results, columns=["Compound", "Weight (g/mol)", "Volume (L)", "Concentration (M)", "Mass (g)"])
        st.write(result_df)
    else:
        st.error("No calculations to display.")
