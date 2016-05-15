import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here

        # initialize Q-matrix
        self.Qmat = {}
        
        # initialize other variables
        self.gamma = 0.9
        self.alpha = 0.5

        # This function reaches at the very beginning of the script

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        self.serial = 0
        
        # This function reaches at every start of a new trial

    def update(self, t):
        # ----------------------------- check information from previous time step
        self.prev_waypoint = self.next_waypoint

        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)
        
        #print self.prev_waypoint, self.next_waypoint

        # TODO: Update state
        # self.state = (inputs['light'], self.next_waypoint, deadline)
        self.state = (inputs['light'], self.next_waypoint)
        self.serial += 1
        
        # To see if serial number continues after the agent reaches destination.
        print self.serial

        # TODO: Select action according to your policy
        if self.state in self.Qmat.keys():
    	    print "-------------------------------------- yes"
    	    action_key_value = self.Qmat[self.state]  # this shows key/value of selected state in Qmat
    	    action = max(action_key_value, key = action_key_value.get) # select action of highest probability
    	    # action = self.next_waypoint
    	else:
    		print "---------------------- no"
    		#self.Qmat[self.state] = 'dummy'
    		self.Qmat[self.state] = {None:0, 'forward':0, 'left':0, 'right':0}

    		# random action, when landed on a 'new' state
    		action = random.choice([None, 'forward','left','right'])
        
        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward

        # Q(s',a') based on selected action


        # New state definition seems incorrect
        # new_state = (inputs['light'],action,deadline-1)
        new_state = (inputs['light'],action)
        print self.state
        print new_state

        if new_state in self.Qmat.keys():
        	Q_nextT = max(self.Qmat[new_state].values())
        else:
        	Q_nextT = 0.
        
        Qhat = (1-self.alpha)*self.Qmat[self.state][action] + (self.alpha*(reward+self.gamma*Q_nextT))
        self.Qmat[self.state][action] = Qhat
        # print "Qhat={}, Q_nextT={}, action={}, NWP={}".format(Qhat,Q_nextT,action,self.next_waypoint)
        
        	
 

        #print "next_waypoint={},action = {},inputs={}".format(self.next_waypoint, action ,inputs)
        # print "next_waypoint={},A = {}, inputs={},R={}".format(self.next_waypoint, action,inputs ,reward)
        # print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # set agent to track
	
	# Now simulate it
    sim = Simulator(e, update_delay=1.0/10.)  # reduce update_delay to speed up simulation
    sim.run(n_trials=10)  # press Esc or close pygame window to quit

if __name__ == '__main__':
    run()
