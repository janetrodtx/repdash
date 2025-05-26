import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Load data
@st.cache_data

def load_data():
    summary_df = pd.read_csv("may1.csv", skiprows=4)
    performance_df = pd.read_csv("may2.csv", skiprows=4)
    attendance_df = pd.read_csv("Attendance Enhanced (AMPM)-Table 1.csv", index_col=0)
    checkins_df = pd.read_csv("Daily Check-Ins-Table 1.csv")
    missed_days_df = pd.read_csv("Missed Days-Table 1.csv")
    summary_stats_df = pd.read_csv("Monthly Summary-Table 1.csv")
    return summary_df, performance_df, attendance_df, checkins_df, missed_days_df, summary_stats_df

summary_df, performance_df, attendance_df, checkins_df, missed_days_df, summary_stats_df = load_data()

# App title
st.title("May 2025 Sales, Attendance & Rep Performance Dashboard")

# Sidebar for view selection
view_option = st.sidebar.selectbox("Select View", ["Daily Totals", "Month-to-Date Totals", "Rep Productivity", "Attendance Overview"])

# DAILY TOTALS VIEW
if view_option == "Daily Totals":
    st.subheader("Daily Totals")
    st.dataframe(summary_df)

# MONTH-TO-DATE TOTALS VIEW
elif view_option == "Month-to-Date Totals":
    st.subheader("Month-to-Date Totals")
    totals_row = summary_df.iloc[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("Leads Assigned", totals_row["Assigned"])
    col2.metric("Messages Sent", totals_row["Unnamed: 6"])
    col3.metric("Calls Fielded", totals_row["Unnamed: 13"])

    col4, col5 = st.columns(2)
    col4.metric("Quotes", totals_row["Unnamed: 14"])
    col5.metric("Deposits", totals_row["Unnamed: 16"])

    st.write("---")
    st.write("### Raw Summary Data")
    st.dataframe(summary_df)

# REP PRODUCTIVITY VIEW
elif view_option == "Rep Productivity":
    st.subheader("Rep Productivity")
    rep_name = st.selectbox("Select Rep", performance_df["Unnamed: 1"].dropna().unique())
    rep_data = performance_df[performance_df["Unnamed: 1"] == rep_name].iloc[0]

    # Attendance linkage
    if rep_name in attendance_df.index:
        rep_attendance = attendance_df.loc[rep_name]
        days_present = rep_attendance[rep_attendance.str.startswith("✔️")].count()
        total_days = rep_attendance[rep_attendance != "⚪️ Off"].count()
        attendance_ratio = days_present / total_days if total_days > 0 else 0
        st.metric("Attendance Rate", f"{attendance_ratio:.0%}")

        # Attendance vs. performance plot with toggle
        stat_option = st.radio("Compare against", ["Leads", "Quotes", "Messages", "Calls"])
        dates = attendance_df.columns
        presence_status = [1 if val.startswith("✔️") else 0 for val in rep_attendance.values]

        if stat_option == "Leads":
            value = rep_data["Leads Assigned"]
            color = 'green'
            label = 'Avg Leads/Present Day'
        elif stat_option == "Quotes":
            value = rep_data["Sensei Quotes"]
            color = 'blue'
            label = 'Avg Quotes/Present Day'
        elif stat_option == "Messages":
            value = rep_data["Msgs Sent"]
            color = 'purple'
            label = 'Avg Msgs/Present Day'
        else:
            value = rep_data["Calls Fielded"]
            color = 'orange'
            label = 'Avg Calls/Present Day'
            value = rep_data["Sensei Quotes"]
            color = 'blue'
            label = 'Avg Quotes/Present Day'

        average_value = value / sum(presence_status) if sum(presence_status) > 0 else 0

        st.write("---")
        st.write("### Attendance vs Performance")
        fig2, ax2 = plt.subplots()
        ax2.plot(dates, presence_status, marker='o', label='Present (1=Yes)')
        ax2.axhline(y=average_value, color=color, linestyle='--', label=label)
        ax2.set_xticklabels(dates, rotation=45, ha='right')
        ax2.set_title(f"Daily Attendance vs {stat_option}")
        ax2.legend()
        st.pyplot(fig2)

    st.metric("Leads Assigned", rep_data["Leads Assigned"])
    st.metric("Messages Sent", rep_data["Msgs Sent"])
    st.metric("Calls Fielded", rep_data["Calls Fielded"])
    st.metric("Quotes", rep_data["Sensei Quotes"])

    st.write("---")
    fig, ax = plt.subplots()
    sns.barplot(x=["Leads", "Msgs", "Calls", "Quotes"],
                y=[rep_data["Leads Assigned"],
                   rep_data["Msgs Sent"],
                   rep_data["Calls Fielded"],
                   rep_data["Sensei Quotes"]],
                ax=ax)
    ax.set_title(f"Activity Breakdown for {rep_name}")
    st.pyplot(fig)

# ATTENDANCE VIEW
elif view_option == "Attendance Overview":
    st.subheader("Attendance Overview")
    selected_rep = st.selectbox("Select Rep", attendance_df.index)
    rep_attendance = attendance_df.loc[selected_rep]

    present_days = rep_attendance[rep_attendance.str.startswith("✔️")]
    absent_days = rep_attendance[rep_attendance == "❌"].count()
    off_days = rep_attendance[rep_attendance == "⚪️ Off"].count()
    checked_unplanned = rep_attendance[rep_attendance == "🟡 Checked In"].count()

    st.metric("Days Present", len(present_days))
    st.metric("Missed Days", absent_days)
    st.metric("Scheduled Off", off_days)
    st.metric("Unscheduled Check-ins", checked_unplanned)

    st.write("---")
    st.write("### Raw Attendance Data")
    st.dataframe(rep_attendance.to_frame(name="Status"))

    st.write("---")
    st.write("### Team Check-In Overview")
    st.line_chart(checkins_df.set_index("Date"))

    st.write("### Missed Days by Rep")
    st.bar_chart(missed_days_df.set_index("Rep"))

    st.write("### Monthly Summary")
    st.dataframe(summary_stats_df)

st.write("mbo")("Built with Streamlit | Data from May 1–23, 2025")

