import math
import streamlit as st

from datetime import date
from datetime import datetime as dt

from time_model import (
    TOTAL_WORKING_HOURS_IN_WEEK, MAX_NUMBER_OF_MEETINGS, 
    TOTAL_WORKING_HOURS_IN_DAY, ROUNDING_DEFAULT,
    get_week_start, calc_average_meeting_length, calc_average_meeting_block_length,
    calc_productive_time_lost, calc_potential_productive_time, calc_lost_productivity, 
    calc_meeting_time
    )

menu_items = {
        'About': "This is an app about analysing your productive working time!"
    }
title = 'Lets talk about meetings...'
st.set_page_config(page_title=title, page_icon='⏰', layout="centered", initial_sidebar_state="auto", menu_items=menu_items)


####################################################################################################################

st.title(title)

st.write('This model captures the interaction effects of meetings on productive time in a week.')

date_input = st.date_input(
    'Select A Week To Analyse',
    value=dt.today(), min_value=date(2022, 1, 1), max_value=date(2023, 1, 1))

st.caption(f'Week commencing {get_week_start(date_input)}')

####################################################################################################################

st.subheader('Parameters section')

required_productive_proportion = st.slider(
    label='What proportion of time do you need to do productive work this week? (%)',
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
        max_value=TOTAL_WORKING_HOURS_IN_WEEK, 
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
st.write('''\* _A meeting block is a series of back-to-back meetings separated by no more than 5 minutes. You should have less meeting blocks than meetings._''')
st.write('''\* _Context switching refers to time it takes you to get back into a productive working mode. The average cost of context switching is 22 minutes and varies depending on the type of task you are undertaking._''')

####################################################################################################################

st.subheader('Results section')

col1, col2 = st.columns(2)

with col1:
    val = calc_meeting_time(input_total_meeting_hours, input_total_meetings)
    st.metric(
        label='Total meeting time (hours)', 
        value=input_total_meeting_hours, 
        #delta=float, 
        delta_color="normal")

with col2:
    val = calc_meeting_time(input_total_meeting_hours, input_total_meetings, True) 
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
    av_block_length = calc_average_meeting_block_length(input_total_meeting_hours, input_total_meeting_blocks) 
    st.metric(
        label='Average meeting block duration (mins)', 
        value=round(av_block_length, 0),
        #delta=float, 
        delta_color="normal")

col1, col2 = st.columns(2)

with col1:
    lost_productivity = calc_lost_productivity(input_total_meeting_blocks, input_context_switch_cost_mins)
    st.metric(
        label='Lost productivity (hours)', 
        value=round(lost_productivity, 1), 
        #delta=float, 
        delta_color="normal")

with col2:
    lost_productivity_prop = calc_lost_productivity(input_total_meeting_blocks, input_context_switch_cost_mins, True)
    st.metric(
        label='Lost productivity (%)', 
        value= f'{lost_productivity_prop:.00%}', 
        #delta=float, 
        delta_color="normal")

col1, col2 = st.columns(2)

with col1:
    productive_time_lost = calc_productive_time_lost(input_total_meeting_hours, input_total_meeting_blocks, input_context_switch_cost_mins) 
    st.metric(
        label='Non-working time (hours)', 
        value=round(productive_time_lost, 1), 
        #delta=float, 
        delta_color="normal")

with col2:
    productive_time_lost_prop = calc_productive_time_lost(input_total_meeting_hours, input_total_meeting_blocks, input_context_switch_cost_mins, True) 
    st.metric(
        label='Non-working time (%)', 
        value=f'{productive_time_lost_prop:.00%}', 
        #delta=float, 
        delta_color="normal")

col1, col2 = st.columns(2)

with col1:
    productive_time = calc_potential_productive_time(input_total_meeting_hours, input_total_meeting_blocks, input_context_switch_cost_mins)
    st.metric(
        label='Potential productive time (hours)', 
        value=round(productive_time, 1), 
        #delta=float, 
        delta_color="normal")

with col2:
    productive_time_prop = calc_potential_productive_time(input_total_meeting_hours, input_total_meeting_blocks, input_context_switch_cost_mins, True)
    st.metric(
        label='Potential productive time (%)', 
        value= f'{productive_time_prop:.00%}', 
        #delta=float, 
        delta_color="normal")

####################################################################################################################

st.subheader('Reccomendations')

st.write(f'You stated that you require {required_productive_proportion}% of your working week to be productive working time.')

required_productive_proportion_calc = required_productive_proportion / 100
balance_of_productive_time = required_productive_proportion_calc - productive_time_prop
amount_of_time_required = round(balance_of_productive_time * TOTAL_WORKING_HOURS_IN_DAY, ROUNDING_DEFAULT)
av_meeting_length = calc_average_meeting_length(input_total_meeting_hours, input_total_meetings)
meetings_to_cut = (amount_of_time_required * 60) / list({av_meeting_length or 1})[0]
meetings_to_cut_lower = math.floor(meetings_to_cut)
meetings_to_cut_higher = math.ceil(meetings_to_cut)

deficit_text = f'''
\n The bad news is...
\n You have a deficit of {amount_of_time_required} hours to meet your productivity target.
\n We therefore reccomend you remove between {meetings_to_cut_lower} and {meetings_to_cut_higher} meeting(s) from your calendar, based
based on an average meeting duration of {av_meeting_length}.
\n Good luck!
'''

surplus_text = f'''
\n Lucky you!
\n You have a surplus of {abs(amount_of_time_required)} hours to meet your productivity target.
\n Your average meeting length is {av_meeting_length} minutes.
\n You do not need to remove any meetings.
\n You can probably use the extra time to make more progress on your work, take a long lunch, read a book, or simply do nothing.
'''

chosen_text = 'Complete parameter settings above to produce reccomendations'
deficit_sign = ''

img_path = "images/waiting.png"
if amount_of_time_required > 0:
    chosen_text = deficit_text
    img_path = "images/stressed.png"
    
if amount_of_time_required <= 0:
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
        label='Time required to meet productivity target (hours)', 
        value= f'{round(amount_of_time_required, 1)}', 
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

with st.expander("Research"):
    st.write("""Research shows that there are many challenges to getting productive work done due to excessive meetings and the costs of context switching""")
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
    \n - [Context Switching: Loom blog](https://www.loom.com/blog/cost-of-context-switching)
    \n - [Context Switching: Developer specific](https://www.brightdevelopers.com/the-cost-of-interruption-for-software-developers/)
    '''
    st.markdown(body, unsafe_allow_html=False)

####################################################################################################################


st.caption('Developed with ❤️ in London.')
