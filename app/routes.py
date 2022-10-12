from flask import render_template, request
from app import app, selectStar, writeSchedule
from app.forms import ScheduleForm, StarSelectForm, ResetImageForm
from exposureTimeCalculator import expose
import pandas as pd
import os
import aplpy
from datetime import datetime
from astroquery.skyview import SkyView
from astropy import units as u

@app.route('/', methods=['GET', 'POST'])
def index():
    #Renders up-to-date star selection graphic
    try:
        #If the image is over 5 hours old, regenerates it
        if (datetime.now().timestamp()
            - os.path.getmtime('./app/static/plot.png') > 18000):
            selectStar()
    except: #If image doesn't exist, creates it
        selectStar()
    
    starField = ''
    
    #Imports list of stars
    star_list = pd.read_csv('app/static/StarList.txt', sep="\t")
    star_list = star_list.values.flatten().tolist()
    
    #Creates forms
    sched_form = ScheduleForm()
    star_form = StarSelectForm()
    reset_form = ResetImageForm()
    
    #Sets drop down list values to be our list of possible stars
    star_form.select_star.choices = star_list
    
    #Creates list of default values to send to form after new star is selected
    defaults = []
    path = [[]]
    
    if reset_form.submitReset.data and reset_form.validate():
        selectStar()
        print("Star selection graphic reset")
    
    #If a star was just selected run this:
    if star_form.submitStar.data and star_form.validate():
        print("Star selected")
        selected_star = request.form.get('select_star')
        selected_filters = request.form.get('select_filters')
        
        #Imports star info from our data file on all possible stars
        data_file_name = './app/static/PVMS_RR_Lyrae_Candidates.csv'
        data_file = open(data_file_name)
        df = pd.read_csv(data_file)
        data_file.close()
        
        #Generates relevant information for just the selected star
        select_star_df = df.where(df["Name"] == (selected_star + ' ')).dropna()
        RA = select_star_df["RA (deg)"].values[0]
        DE = select_star_df["DE (deg)"].values[0]
        mag = select_star_df["Min I"].values[0]
        
        #Generates string of exposure times for default value in form
        duration = ""
        filterstring = ""
        for individual_filter in selected_filters.split(','):
            #Checks if each filter is part of our list of valid filters
            if individual_filter in ["B", "V", "R", "I", "H", "U"]:
                time = round(expose(individual_filter,mag))
                duration += str(time) + ","
                filterstring += str(individual_filter)
            else:
                print("Invalid filter chosen: " + individual_filter)
        
        #Removes final trailing comma on duration string
        if len(duration) > 0:
            duration = duration[:-1]
        
        #Adds information to default values list
        defaults.append('./app/static/schedules/'
                        + selected_star.replace(' ','')
                        + '_' + filterstring + '.sch')
        defaults.append(selected_star)
        defaults.append(RA)
        defaults.append(DE)
        defaults.append(selected_filters)
        defaults.append(duration)
        
        #Gets fits data for star field around selected object
        path = SkyView.get_images(position=str(RA) + ' ' + str(DE),
                                  survey=['DSS'], pixels=500,
                                  height=20*u.arcmin, width=20*u.arcmin)
        
        #Saves fits data to png file
        gc = aplpy.FITSFigure(path[0][0])
        gc.show_grayscale()
        gc.save('app/static/starField.png')
        gc.close()
        starField = '/static/starField.png'
    
    #If sched_form has been submitted, creates schedule file
    if sched_form.submitSched.data and sched_form.validate():
        inputs = [sched_form.title.data, sched_form.observer.data, sched_form.source.data,
                  sched_form.ra.data, sched_form.dec.data, sched_form.epoch.data,
                  sched_form.lststart.data, sched_form.filters.data, sched_form.duration.data,
                  sched_form.binning.data, sched_form.subimage.data, sched_form.priority.data,
                  sched_form.compress.data, sched_form.imagedir.data, sched_form.ccdcalib.data,
                  sched_form.shutter.data, sched_form.repeat.data]
        writeSchedule(sched_form.fileName.data, inputs)
        print("Schedule file written")
    
    #Renders page
    return render_template('graph.html', starSelectGraphic='/static/plot.png',
                           starField = starField,
                           sched_form=sched_form, reset_form=reset_form,
                           star_form=star_form, star_list=star_list,
                           defaults=defaults)