# Direct a silent vertical cartoon

From the supplied Sinhala or English story, write a visual setup, escalation and payoff. Use five-second shots where that rhythm works. Describe which character looks where, the contact point of each prop, a readable hold before the reveal, and how the next shot continues the pose.

Read story.json and art.cjs. For a new story, author the needed SVG shapes, expressions, effects and temporal curves in art.cjs. Changing the prompt field alone does not change the drawing. Retain stable silhouettes for recurring characters. Use layer-local coordinates and keep held props at the hand. Expose new timing and camera controls in story.json. Keep the functional interface svg(story,time,layer,flat). No remote images or network calls inside a frame. Keep still poses expressive. Render using render.py, inspect a contact sheet, and verify duration and video streams before delivery.
