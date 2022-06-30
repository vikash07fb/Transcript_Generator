import csv
import os
from fpdf import FPDF
from datetime import datetime
import streamlit as st
import pandas as pd



#have to update for new branches and mtech/msc/phd course
course={}
course["CS"]="Computer Science and Engineering"
course["EE"]="Electrical and Electronics Engineering"
course["ME"]="Mechanical Engineering"
course["CE"]="Civil and Environmental Engineering"
course["CB"]="Chemical and Biochemcial Engineering"
course["MM"]="Metallurgical and Material Engineering"

program={}
program["01"]="Bachelor of Technology"
program["11"]="Master of Technology"
program["12"]="Master of Science"
program["21"]="Doctor of Philosophy"

grade_value={}
grade_value["AA"]=10
grade_value["AB"]=9
grade_value["BB"]=8
grade_value["BC"]=7
grade_value["CC"]=6
grade_value["CD"]=5
grade_value["DD"]=4
grade_value["F"]=0


global total_credit_taken
global previous_cpi
total_credit_taken=0
previous_cpi=0
SUBJECTS = {}
Name_Rollno ={}
student={}

class semester:

    credit_taken=0
    credit_clear=0
    spi=0
    cpi=0
    def __init__(self,subjects):
        self.subjects=subjects
        self.credit_taken=0
        
    def get_ct(self):
        total_credit=0
        for sub in self.subjects:
            total_credit+=int(SUBJECTS[sub[0]]["crd"])
        self.credit_taken= total_credit
    
    def get_cc(self):
        credit_cleared=0
        for sub in self.subjects:
            if sub[1]!="F":
                credit_cleared+=int(SUBJECTS[sub[0]]["crd"])
        self.credit_clear=credit_cleared
                
    def get_spi(self):
        spi=0
        for sub in self.subjects:
            sub[1] = sub[1].strip()
            curr_grade = sub[1]
            if curr_grade[-1] == '*':
                curr_grade = curr_grade[:-1]
            if curr_grade!="F":
                spi += int(grade_value[curr_grade]) * int(SUBJECTS[sub[0]]["crd"])
        spi /= self.credit_taken
        spi = int((spi * 100) + 0.5) / 100.0
        self.spi = spi
    
    def get_cpi(self):
        global total_credit_taken
        global previous_cpi
        cpi = (previous_cpi * total_credit_taken) + (self.spi * self.credit_taken)
        cpi /= (total_credit_taken + self.credit_taken)
        total_credit_taken += self.credit_taken
        cpi = int((cpi * 100) + 0.5) / 100.0
        previous_cpi = cpi
        self.cpi = cpi
    
    def info(self):
        self.get_ct()
        self.get_cc()
        self.get_spi()
        self.get_cpi()


class student_info:
    def __init__(self, name, roll_no, program, year, course, semesters):
        self.name = name
        self.roll_no = roll_no
        self.program = program
        self.year = year
        self.course = course
        self.semesters = semesters
        #print(semesters)
        self.A3 = 0
        if self.program[0] == 'B':
            self.A3 = 1
            
    def draw_margins(pdf, left_x, right_x, top_y, bottom_y):
        pdf.set_line_width(0.5)
        pdf.set_draw_color(r=0,g=0,b=0)
        pdf.line(x1=left_x,x2=right_x,y1=top_y,y2=top_y)
        pdf.line(x1=left_x,x2=right_x,y1=bottom_y,y2=bottom_y)
        pdf.line(x1=left_x,x2=left_x,y1=top_y,y2=bottom_y)
        pdf.line(x1=right_x,x2=right_x,y1=top_y,y2=bottom_y)
        
    def create_table(curr_sem,pdf,start_x,start_y,sem,a3):
        curr_x = start_x
        curr_y = start_y

        col_width = [16,55,8,8,8] if a3 else [15,50,8,8,8]
        line_height = 4 if a3 else 3
        font = "Times"
        font_size = 6.5 if a3 else 5.5
        heading_font_size = 15 if a3 else 11
        table_heading_w = 50
        table_heading_h = 10 if a3 else 7
        cols = ["Sub. Code","Subject Name","L-T-P","CRD","GRD"]

        #TODO: Put real data
        pdf.set_xy(x=curr_x,y=curr_y)
        pdf.set_font(size=heading_font_size)
        pdf.multi_cell(table_heading_w, table_heading_h, sem, border=0, ln=3, align= 'L',markdown=True)
        pdf.ln()

        if curr_sem.subjects:
            pdf.set_font(font,size=font_size,style="B")
            pdf.set_x(curr_x)
            for j in range(5):
                pdf.multi_cell(col_width[j], line_height, cols[j], border=1, ln=3, align= 'C',markdown=True)
            pdf.ln()
            pdf.set_x(start_x)
            pdf.set_font(font,size=font_size,style="")

            for curr_sub in curr_sem.subjects:
                row=[curr_sub[0],SUBJECTS[curr_sub[0]]["subname"],SUBJECTS[curr_sub[0]]["ltp"],SUBJECTS[curr_sub[0]]["crd"],curr_sub[1]]
                for j in range(len(row)):
                    pdf.multi_cell(col_width[j], line_height, str(row[j]), border=1, ln=3, align= 'C',markdown=True)
                pdf.ln()
                pdf.set_x(curr_x)

            pdf.set_y(pdf.get_y()+3)
            pdf.set_x(start_x)
            bottom_text = "**"+"Credits Taken: "+str(curr_sem.credit_taken) +"     "+"Credits Cleared: "+str(curr_sem.credit_clear)+"     "+"SPI: "+ str(curr_sem.spi) +"     "+"CPI: "+str(curr_sem.cpi)+"**"
            pdf.multi_cell(col_width[0]+col_width[1],line_height+1,bottom_text,border=1,ln=3,align="J",markdown=True)

    def create_header1(pdf,left_x,right_x,top_y):
        file_name = "header1_v2.png"
        header1_x = left_x+1
        header1_y = top_y+1
        header1_w = right_x-left_x-2
        header1_h = 40-2

        pdf.set_xy(header1_x,header1_y)
        pdf.image(w=header1_w, name=file_name)

    def create_header2(self,pdf,header2_x,header2_y,header2_w,header2_h):
        tab = "                "
        header2_string = "**Roll Number:** "+self.roll_no + tab + "**Name:** "+self.name + tab + "**Year of Admission:** "+self.year +"\n"
        header2_string += "**Programme:** "+self.program + tab + "**Course:** "+self.course 
        pdf.set_xy(header2_x,header2_y)
        pdf.multi_cell(header2_w,header2_h/2,header2_string,border=1,ln=3,align="L",markdown=True)

    def insert_stamp(pdf,stamp_pos_x,stamp_pos_y,stamp_w,stamp_h,file_name):
        pdf.set_xy(stamp_pos_x,stamp_pos_y)
        pdf.image(name=file_name,h=stamp_h,w=stamp_w)

    def create_footer(pdf,left_x,right_x,bottom_y,want_seal,a3):
        dog_x = left_x+5
        dog_y = bottom_y-10
        dog_h = 5
        dog_w = 150

        sign_x = right_x-70
        sign_y = bottom_y-10
        sign_w = 70
        sign_h = 5

        line_x1 = sign_x
        line_x2 = sign_x+sign_w-10
        line_y1 = sign_y-2
        line_y2 = line_y1
        
        font = "Times"
        font_size = 12

        pdf.set_xy(dog_x,dog_y)
        pdf.set_font(font,size=font_size,style="B")
        date_text = "Date of Generation: "+ datetime.now().strftime("%d/%m/%Y %H:%M")
        pdf.multi_cell(dog_w, dog_h, date_text, border=0, ln=3, align= 'L',markdown=True)

        pdf.set_xy(sign_x,sign_y)
        pdf.multi_cell(sign_w,sign_h,"Asssistant Registrar (Academic)")
        
        signi_x=sign_x+5
        signi_y=(line_y1-27) if a3 else (line_y1-18)
        signi_w=30 if a3 else 20
        signi_h=30 if a3 else 20
        
        signi_filename="signature.png"
        pdf.set_xy(signi_x,signi_y)
        if want_seal:
            pdf.image(name=signi_filename,h=signi_h,w=signi_w)
        
        pdf.line(x1=line_x1,x2=line_x2,y1=line_y1,y2=line_y2)

    def create_transcript(self,want_seal):
        a3=self.A3
        file_name = "transcriptsIITP/"+self.roll_no+".pdf"
        page_size = "A3" if a3 else "A4"
        left_m = 5
        left_x = left_m
        right_m = 5
        right_x = 420-right_m if a3 else 297-right_m
        top_m = 5
        top_y = top_m
        bottom_m = 5
        bottom_y = 297-bottom_m if a3 else 210-bottom_m
        add_stamp = want_seal

        font = "Times"
        font_size = 15 if a3 else 10

        pdf = FPDF(orientation="landscape", format=page_size)
        pdf.add_page()
        pdf.set_font(font,size=font_size)
        pdf.set_margins(left=left_m,right=right_m,top=top_m)
        pdf.set_auto_page_break(False)
        student_info.draw_margins(pdf,left_x,right_x,top_y,bottom_y)

        student_info.create_header1(pdf,left_x,right_x,top_y)

        curr_x = pdf.get_x()
        curr_y = pdf.get_y()

        header2_w = 250 if a3 else 170
        header2_h = 15 if a3 else 12
        header2_x = 85 if a3 else 60
        header2_y = curr_y + 5

        student_info.create_header2(self,pdf,header2_x,header2_y,header2_w,header2_h)

        partition_1 = header2_y+header2_h+(76.5 if a3 else 65)
        partition_2 = (partition_1+70) if a3 else partition_1

        pdf.set_line_width(0.5)
        pdf.set_draw_color(r=0,g=0,b=0)
        if len(self.semesters)>4:
            pdf.line(x1=left_x,x2=right_x,y1=partition_1,y2=partition_1)
        if len(self.semesters)>8:
            pdf.line(x1=left_x,x2=right_x,y1=partition_2,y2=partition_2)   


        start_x = [left_x+5,left_x+105,left_x+205,left_x+305] if a3 else [left_x+5,left_x+99,left_x+193]
        start_y = [header2_y+header2_h,partition_1,partition_2] if a3 else [header2_y+header2_h+5,partition_1+5,partition_2+5]
        row_lim = len(start_x)
        for curr_sem in range (len(self.semesters)):
            sem_string = "**--Semester "+str(curr_sem+1)+"--**"
            student_info.create_table(self.semesters[curr_sem],pdf,start_x[(curr_sem)%row_lim],start_y[(curr_sem)//row_lim],sem_string,a3)

        stamp_pos_x = start_x[3]+10 if a3 else start_x[1]
        stamp_pos_y = start_y[2]+10 if a3 else start_y[2]+45
        stamp_w = 35 if a3 else 25
        stamp_h = 35 if a3 else 25
        stamp_name = "stamp.png"
        student_info.create_footer(pdf,left_x,right_x,bottom_y,want_seal,a3)
        if add_stamp:
            student_info.insert_stamp(pdf,stamp_pos_x,stamp_pos_y,stamp_w,stamp_h,stamp_name)
        pdf.output(file_name)

        
#global output_string
output_string="Transcript not Found for: "

def read_files():
    subjects_file = open('subjects_master.csv')
    reader = csv.DictReader(subjects_file)
    students_file_grade = open('grades.csv')
    grade = csv.DictReader(students_file_grade)
    students_file_rollno = open('names-roll.csv')
    name_rollno = csv.DictReader(students_file_rollno)

    global SUBJECTS
    global Name_Rollno
    global student
    for row in reader:
        SUBJECTS[row['subno']] = {
            'subname': row['subname'],
            'ltp': row['ltp'],
            'crd': row['crd'],
        }

    for row in name_rollno:
        Name_Rollno[row['Roll']]=row['Name']


    grade = sorted(grade, key=lambda row:(row['Roll'],int(row['Sem']),row['SubCode']), reverse=False)

    student_roll= grade[0]['Roll']
    count= len(grade)
    i=0

    while(i<count):
        global total_credit_taken
        global previous_cpi
        total_credit_taken=0
        previous_cpi=0
        prev_sem=0
        if grade[i]['Roll']==student_roll:
            semesters=[]
            while(i<count and grade[i]['Roll']==student_roll):
                subjects=[]
                sem=grade[i]['Sem']
                while prev_sem+1!=int(sem):
                    prev_sem+=1
                    subject_1={}
                    curr_sem_1=semester(subject_1)
                    semesters.append(curr_sem_1)
                while(i<count and grade[i]['Sem']==sem):
                    subjects.append([grade[i]['SubCode'],grade[i]['Grade']])
                    i+=1
                prev_sem+=1
                curr_sem=semester(subjects)
                curr_sem.info()
                semesters.append(curr_sem)
                if(i<count):
                    sem=grade[i]['Sem']
            student[student_roll]=student_info(Name_Rollno[student_roll],student_roll,program[student_roll[2:4]],"20"+student_roll[:2],course[student_roll[4:6]],semesters)
            if(i<count):
                student_roll=grade[i]['Roll']

def create_pdf(start,end,want_seal):
    global output_string
    if start[:6]!=end[:6] or int(start[6:8])>int(end[6:8]):
         st.error("Error")
    else:
        read_files()
        for rollno in range (int(start[6:8]),int(end[6:8])+1):
            roll_no=start[0:6]
            if(rollno<10):
                roll_no=roll_no + '0'
            roll_no=roll_no +str(rollno)

            if roll_no in student:
                if want_seal=="1" or want_seal==1:
                    student[roll_no].create_transcript(1)
                else:
                    student[roll_no].create_transcript(0)
            else:
                output_string=output_string + roll_no +" "
        if len(output_string)>30:
            print(output_string)
            st.error(output_string)    

def create_all_transcript(want_seal):
    read_files()
    if want_seal=="1" or want_seal==1:
        for key in student:
            student[key].create_transcript(1)
    else: 
        for key in student:
            student[key].create_transcript(0)




#Frontend
st.title("""
TRANSCRIPT GENERATOR
""")
st.write("")
st.write("Browse for files")

grades_csv = st.file_uploader("Upload Grades.csv")
if (grades_csv):
    dataframe = pd.read_csv(grades_csv)
    dataframe.to_csv("grades.csv")

st.write("")
st.write("")
st.write("Browse for files")

roll_no = st.file_uploader("Upload Roll Number.csv")
if (roll_no):
    dataframe = pd.read_csv(roll_no)
    dataframe.to_csv("names-roll.csv")

st.write("")
st.write("")
st.write("Browse for files")
subject = st.file_uploader("Upload Masters Subjects.csv")
if (subject):
    dataframe = pd.read_csv(subject)
    dataframe.to_csv("subjects_master.csv")
st.write('Enter starting and Ending Roll No.:')
st.write('')
start_roll = st.text_input('starting roll')
end_roll = st.text_input('end roll')
my_slot1 = st.empty()

want_seal=False
want_seal = st.checkbox('include stamp and signature', value=False, key=None, help=None, on_change=None, args=None, kwargs=None)
st.button('Print Transcript', key=None, help=None, on_click=create_pdf, args=(start_roll,end_roll,want_seal), kwargs=None)
st.button('Print All Transcript', key=None, help=None, on_click=create_all_transcript,args=(want_seal,))

