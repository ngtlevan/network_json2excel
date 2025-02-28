import streamlit as st
import pandas as pd
import json
import io

def convert_post_count(post_str):
    """Convert formatted post count (e.g., '3.2M', '1K') to integer."""
    if isinstance(post_str, str):
        post_str = post_str.upper()
        if 'M' in post_str:
            return int(float(post_str.replace('M', '')) * 1_000_000)
        elif 'K' in post_str:
            return int(float(post_str.replace('K', '')) * 1_000)
        elif post_str.isdigit():
            return int(post_str)
    return 0  # Default if format is unknown

def process_json(file):
    """Process uploaded JSON file and return two DataFrames."""
    data = json.load(file)
    main_rows = []
    related_rows = []
    fields = ["average", "frequent", "rare", "related", "relatedAverage", "relatedFrequent", "relatedRare"]
    
    for entry in data:
        main_hashtag = entry.get("name", "Unknown")
        num_posts_str = entry.get("posts", "0")
        num_posts = convert_post_count(num_posts_str)
        main_rows.append([main_hashtag, num_posts])
        
        for field in fields:
            if field in entry and isinstance(entry[field], list):
                counter = 1
                for related in entry[field]:
                    related_hashtag = related.get("hash", "").lstrip("#")
                    related_posts = convert_post_count(related.get("info", "0"))
                    related_rows.append([main_hashtag, field, related_hashtag, related_posts, counter])
                    counter += 1
    
    df_main = pd.DataFrame(main_rows, columns=["Main Hashtag", "Number of Posts"])
    df_related = pd.DataFrame(related_rows, columns=["Source", "Type", "Target", "Value", "Position"])
    return df_main, df_related

def convert_df_to_excel(df_main, df_related):
    """Convert DataFrames to an Excel file with two sheets."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_main.to_excel(writer, index=False, sheet_name="Main Hashtags")
        df_related.to_excel(writer, index=False, sheet_name="Related Hashtags")
    processed_data = output.getvalue()
    return processed_data

# Streamlit UI
st.title("JSON to Excel Converter")
st.write("Upload a JSON file to process hashtags and download the result as an Excel file.")

uploaded_file = st.file_uploader("Upload JSON File", type=["json"])

if uploaded_file is not None:
    df_main, df_related = process_json(uploaded_file)
    st.write("### Main Hashtags Data Preview:")
    st.dataframe(df_main)
    st.write("### Related Hashtags Data Preview:")
    st.dataframe(df_related)
    
    excel_data = convert_df_to_excel(df_main, df_related)
    st.download_button(
        label="Download Excel File",
        data=excel_data,
        file_name="hashtags_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
