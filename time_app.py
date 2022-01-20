import math
import streamlit as st

from datetime import date
from datetime import datetime as dt

from time_model import (
    TOTAL_WORKING_HOURS_IN_WEEK, MAX_NUMBER_OF_MEETINGS, 
    TOTAL_WORKING_HOURS_IN_DAY, DAYS_IN_WORKING_WEEK,
    MAX_WORKING_HOURS, MIN_WORKING_HOURS, WARNING_TRIGGER_HOURS,
    get_week_start, calc_average_meeting_length, calc_average_meeting_block_length,
    calc_productive_time_lost, calc_potential_productive_time, calc_lost_productivity, 
    calc_meeting_time, return_working_hours
    )

menu_items = {
        'About': "This is an app about analysing your deep work productive time!"
    }
title = 'Lets talk about meetings...'
st.set_page_config(page_title=title, page_icon='⏰', layout="centered", initial_sidebar_state="auto", menu_items=menu_items)


####################################################################################################################

st.title(title)

intro_text = '''
Meetings are important in our working lives, but they sometimes prevent us from doing deep work.
\n This model captures the interaction effects of meetings on productive deep work time in a week.
'''
st.write(intro_text)

date_input = st.date_input(
    'Select a week in your calendar to analyse',
    value=dt.today(), min_value=date(2022, 1, 1), max_value=date(2023, 1, 1))

week_start = get_week_start(date_input)
input_working_hours_in_week_raw = TOTAL_WORKING_HOURS_IN_WEEK

input_working_hours_in_week_raw = st.number_input(
    label='What is your usual working hours in a week? (8 hour working day (excluding lunch) = 40 hours per week)', 
    min_value=MIN_WORKING_HOURS,
    max_value=MAX_WORKING_HOURS,
    value=float(input_working_hours_in_week_raw),
    step=float(1)
    )

input_working_hours_in_week = return_working_hours(input_working_hours_in_week_raw)

if TOTAL_WORKING_HOURS_IN_WEEK < input_working_hours_in_week <= WARNING_TRIGGER_HOURS:
    st.warning(f'⚠️ Your reported working hours are in excess of {int(TOTAL_WORKING_HOURS_IN_WEEK)} ⚠️ ')

if WARNING_TRIGGER_HOURS < input_working_hours_in_week <= MAX_WORKING_HOURS:
    st.error(f'🚨 Your working hours are in excess of {int(WARNING_TRIGGER_HOURS)} 🚨')

st.caption(f'You chose week commencing: {week_start}')
st.caption(f'We have assumed the following working rhythm: {int(DAYS_IN_WORKING_WEEK)} days a week, {round(input_working_hours_in_week/DAYS_IN_WORKING_WEEK, 1)} working hours a day, {int(input_working_hours_in_week)} hours a week')

####################################################################################################################

st.subheader(f'Add Your Meeting Data For w/c {week_start}')

st.caption('Define some information about your working rhythm.')

required_productive_proportion = st.slider(
    label='What proportion of time do you need to do deep work this week? (%)',
    min_value=0,
    max_value=100,
    step=5,
)

st.caption('Define the parameters below based on your outlook calendar and type of work.')

col1, col2, = st.columns(2)

with col1:
    input_total_meeting_hours = st.slider(
        label='1. Total time spent in meetings (hours)', 
        min_value=float(0), 
        max_value=input_working_hours_in_week, 
        step=float(0.5)
        )

with col2:
    input_total_meetings = st.slider(
        label='2. Total number of meetings', 
        min_value=float(0),
        max_value=MAX_NUMBER_OF_MEETINGS, 
        step=float(1)
        )

col1, col2, = st.columns(2)

with col1:
    input_total_meeting_blocks = st.slider(
        label='3. Total number of meeting blocks *', 
        min_value=float(0),
        max_value=float(max(1, list({input_total_meetings or 0})[0])),
        step=float(1)
    )

with col2:
    input_context_switch_cost_mins = st.slider(
        label='4. Cost of context switching (mins) *', 
        min_value=float(0), 
        max_value=float(30), 
        step=float(1)
    )

help_text = '''
\* _A meeting block is a series of back-to-back meetings separated by no more than 5 minutes. You should have less meeting blocks than meetings._
\n _Context switching refers to time it takes you to get back into a productive working mode. The average cost of context switching is 22 minutes and varies depending on the type of task you are undertaking._
'''
st.markdown(help_text)

####################################################################################################################

st.subheader(f'Your Results For w/c {week_start}')

col1, col2 = st.columns(2)

with col1:
    val = calc_meeting_time(
        total_hours_in_week=input_total_meeting_hours,
        total_meeting_hours=input_total_meetings)
    st.metric(
        label='Total meeting time (hours)',
        value=input_total_meeting_hours,
        #delta=float,
        delta_color="normal")

with col2:
    val = calc_meeting_time(
        total_hours_in_week=input_total_meeting_hours,
        total_meeting_hours=input_total_meetings,
        as_prop=True) 
    st.metric(
        label='Meeting time (%)',
        value=f'{val:.00%}',
        #delta=float,
        delta_color="normal")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        label='Total meeting blocks',
        value=round(input_total_meeting_blocks, 0),
        #delta=float,
        delta_color="normal")

with col2:
    av_block_length = calc_average_meeting_block_length(
        total_meeting_hours=input_total_meeting_hours,
        total_meeting_blocks=input_total_meeting_blocks) 
    st.metric(
        label='Average meeting block duration (mins)',
        value=round(av_block_length, 0),
        #delta=float,
        delta_color="normal")

col1, col2 = st.columns(2)

with col1:
    lost_productivity = calc_lost_productivity(
        total_meeting_blocks=input_total_meeting_blocks,
        context_switch_cost_mins=input_context_switch_cost_mins,
        total_hours_in_week=input_working_hours_in_week)
    st.metric(
        label='Context switching tax (hours)',
        value=round(lost_productivity, 1),
        #delta=float,
        delta_color="normal")

with col2:
    lost_productivity_prop = calc_lost_productivity(
        total_meeting_blocks=input_total_meeting_blocks,
        context_switch_cost_mins=input_context_switch_cost_mins,
        total_hours_in_week=input_working_hours_in_week,
        as_prop=True)
    st.metric(
        label='Context switching tax (%)',
        value= f'{lost_productivity_prop:.00%}',
        #delta=float,
        delta_color="normal")

col1, col2 = st.columns(2)

with col1:
    productive_time_lost = calc_productive_time_lost(
        total_meeting_hours=input_total_meeting_hours,
        total_meeting_blocks=input_total_meeting_blocks,
        context_switch_cost_mins=input_context_switch_cost_mins,
        total_hours_in_week=input_working_hours_in_week) 
    st.metric(
        label='Non-deep work productivity time (hours)',
        value=round(productive_time_lost, 1),
        #delta=float,
        delta_color="normal")

with col2:
    productive_time_lost_prop = calc_productive_time_lost(
        total_meeting_hours=input_total_meeting_hours,
        total_meeting_blocks=input_total_meeting_blocks,
        context_switch_cost_mins=input_context_switch_cost_mins,
        total_hours_in_week=input_working_hours_in_week,
        as_prop=True) 
    st.metric(
        label='Non-deep work productive time (%)',
        value=f'{productive_time_lost_prop:.00%}',
        #delta=float,
        delta_color="normal")

col1, col2 = st.columns(2)

with col1:
    productive_time = calc_potential_productive_time(
        total_meeting_hours=input_total_meeting_hours,
        total_meeting_blocks=input_total_meeting_blocks,
        context_switch_cost_mins=input_context_switch_cost_mins,
        total_hours_in_week=input_working_hours_in_week)
    st.metric(
        label='Deep work productive time (hours)',
        value=round(productive_time, 1),
        #delta=float,
        delta_color="normal")

with col2:
    productive_time_prop = calc_potential_productive_time(
        total_meeting_hours=input_total_meeting_hours,
        total_meeting_blocks=input_total_meeting_blocks,
        context_switch_cost_mins=input_context_switch_cost_mins,
        total_hours_in_week=input_working_hours_in_week,
        as_prop=True)
    st.metric(
        label='Deep work productive time (%)', 
        value= f'{productive_time_prop:.00%}', 
        #delta=float, 
        delta_color="normal")

####################################################################################################################

st.subheader(f'Your Reccomendations For w/c {week_start}')

st.write(f'You stated that you require {required_productive_proportion}% of your working week to be deep work focused productive time.')

required_productive_time = (required_productive_proportion / 100) * input_working_hours_in_week
balance_of_productive_time = round(productive_time - required_productive_time, 1)
av_meeting_length = calc_average_meeting_length(
    total_meeting_hours=input_total_meeting_hours, 
    total_meetings=input_total_meetings)
meetings_to_cut = (balance_of_productive_time * 60) / list({av_meeting_length or 1})[0]
meetings_to_cut_lower = abs(math.ceil(meetings_to_cut))
meetings_to_cut_higher = abs(math.floor(meetings_to_cut))

deficit_text = f'''
\n The bad news is...
\n You have a deficit of {abs(balance_of_productive_time)} hours to meet your deep work productivity target.
\n We therefore reccomend you remove between {meetings_to_cut_lower} and {meetings_to_cut_higher} meeting(s) from your calendar,
based on an average meeting duration of {round(av_meeting_length, 0)}.
\n Remember to remove/reschedule your meetings responsibly! ✌️
\n Good luck!
'''

surplus_text = f'''
\n Lucky you!
\n You have a surplus of {abs(balance_of_productive_time)} hours to meet your deep work productivity target.
\n You do not need to remove any meetings.
\n You can probably use the extra time to make more progress on your work, take a long lunch, read a book, simply do nothing or anything else you choose 😊.
'''

chosen_text = 'Complete parameter settings above to produce reccomendations'
deficit_sign = ''

img_path = "images/waiting.png"
if balance_of_productive_time < 0:
    chosen_text = deficit_text
    img_path = "images/stressed.png"
    
if balance_of_productive_time >= 0:
    chosen_text = surplus_text
    deficit_sign = '(surplus)'
    img_path = "images/relaxed.png"

st.write(chosen_text)


col1, col2 = st.columns(2)
if av_meeting_length <= 0:
    amount_of_time_required = 0
    meetings_to_cut_lower = 0
    meetings_to_cut_higher = 0
with col1:
    st.metric(
        label=f'Time required to meet deep work productivity target (hours) {deficit_sign}', 
        value= f'{abs(balance_of_productive_time)}', 
        #delta=float, 
        delta_color="normal")

with col2:

    st.metric(
        label=f'Reccomended meetings to cut {deficit_sign}', 
        value= f'{meetings_to_cut_lower} to {meetings_to_cut_higher}', 
        #delta=float, 
        delta_color="normal")

st.image(img_path)

####################################################################################################################

with st.expander("Futher Research"):
    st.write("""Research shows that there are many challenges to getting deep work done due to excessive meetings and the costs of context switching""")
    st.write('Advice #1: Each new project brings an overhead of meetings. Try to cut down on the number of projects you are juggling.', unsafe_allow_html=False)
    st.image("images/multitasking.png", caption='Multitasking is costly. Source: RescueTime')
    st.write('Advice #2: Every time you switch meetings, there is a tax your brain pays to get focused on the following task Try to group your meetings into blocks.', unsafe_allow_html=False)
    st.image("images/outlook_cal.png", caption="A random person's outlook calendar. Source: Outlook")
    st.write('Advice #3: Remember to takes breaks, and go for a walks outside and exercise. They will increase your productivity levels in the long run.', unsafe_allow_html=False)
    st.image("images/walk.png", caption="Take a long lunch. Source: Unsplash")
    st.write("Advice #4: Long hours are unsustainable and affect your long term productivity. You can cheat in the very short term, but your body keeps count.", unsafe_allow_html=False)
    st.image("images/working_late.png", caption="Sleep is your friend, know when to call it a day. Source: iStock")
    st.write('References below')
    body = '''
    \n - [VBA script to generate meeting time](https://www.extendoffice.com/documents/outlook/3551-outlook-calendar-count-hours-days-weeks.html)
    \n - [Context Switching: Rescue Time blog](https://blog.rescuetime.com/context-switching/)
    '''
    st.markdown(body, unsafe_allow_html=False)

####################################################################################################################

st.caption('Made with ❤️ in London.')
