
# @author: Panos Patros
# Based on Feedback Control for Computer Systems by Philipp K. Janert (O'Reilly Media)
# COMPX529 Engineering Self-Adaptive Systems

class PIDController:
	def __init__( self, kp, ki, kd):
		self.kp = kp
		self.ki = ki
		self.kd = kd
		self.totalError = 0
		self.prevError = 0
	
	def work( self, e):
		self.totalError += e
	
		up = e*self.kp
		ui = self.totalError*self.ki
		ud = (e-self.prevError)*self.kd
		
		self.prevError = e
		
		return up + ui + ud
