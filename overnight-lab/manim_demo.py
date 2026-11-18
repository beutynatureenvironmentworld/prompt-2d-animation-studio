"""Pure-code Manim 2D motion-graphics character demo."""
from manim import *
config.pixel_width=360
config.pixel_height=640
config.frame_width=4.5
config.frame_height=8
config.frame_rate=15
config.background_color="#fff4df"

class MilkCartonMotion(Scene):
    def construct(self):
        girl=VGroup(
            Circle(radius=.49,stroke_color=BLACK,stroke_width=7,fill_color=WHITE,fill_opacity=1),
            Dot([-0.16,.06,0],radius=.037,color=BLACK),
            Dot([.16,.06,0],radius=.037,color=BLACK),
            Arc(radius=.18,angle=PI,stroke_color=BLACK,stroke_width=5).shift(DOWN*.17)
        ).move_to(LEFT*1.1+UP*.6)
        boy=VGroup(
            Circle(radius=.49,stroke_color=BLACK,stroke_width=7,fill_color=WHITE,fill_opacity=1),
            Dot([-0.16,.06,0],radius=.037,color=BLACK),
            Dot([.16,.06,0],radius=.037,color=BLACK),
            Arc(radius=.18,angle=PI,stroke_color=BLACK,stroke_width=5).shift(DOWN*.17)
        ).move_to(RIGHT*1.1+UP*.6)
        pigtail1=Circle(radius=.18,color=BLACK,stroke_width=6,fill_color=WHITE,fill_opacity=1).next_to(girl,LEFT,buff=-.03).shift(UP*.2)
        pigtail2=Circle(radius=.18,color=BLACK,stroke_width=6,fill_color=WHITE,fill_opacity=1).next_to(girl,RIGHT,buff=-.03).shift(UP*.2)
        dress=Polygon([-1.47,-.09,0],[-.73,-.09,0],[-.50,-1.28,0],[-1.70,-1.28,0],color=BLACK,
          stroke_width=6,fill_color="#fa6482",fill_opacity=1)
        shirt=RoundedRectangle(width=.97,height=1.2,corner_radius=.18,color=BLACK,
          fill_color="#85bdff",fill_opacity=1,stroke_width=6).move_to(RIGHT*1.1+DOWN*.68)
        carton=Rectangle(width=.75,height=.58,color=BLACK,stroke_width=6,fill_color=WHITE,fill_opacity=1).move_to(DOWN*.25)
        straw=Line(carton.get_left()+UP*.10,carton.get_left()+LEFT*.3+UP*.17,color="#75d6fb",stroke_width=9)
        jet=Line(straw.get_end(),girl.get_center()+DOWN*.10,color="#c5f6ff",stroke_width=14)
        self.add(dress,shirt,girl,boy,pigtail1,pigtail2,carton,straw)
        self.wait(.6)
        self.play(Circumscribe(carton,color=YELLOW),run_time=.8)
        self.play(carton.animate.scale(.86),run_time=.35)
        self.play(Create(jet),run_time=.65)
        self.play(girl.animate.shift(LEFT*.18),boy.animate.shift(RIGHT*.12),run_time=.45)
        self.wait(.45)
