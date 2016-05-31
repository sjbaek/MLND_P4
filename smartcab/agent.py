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
        self.alpha = 0.8
        self.gamma = 0.2
        self.epsilon = 0.4

        #self.success = 0.

        # This function reaches at the very beginning of the script

        # Open a csv file to record the agent's success rate

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # This function reaches at every start of a new trial

        # TODO: Prepare for a new trip; reset any variables here, if required
        #self.serial = 0

    def update(self, t):
        # ----------------------------- check information from previous time step
        
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)
        
        # print "inputs    ={}".format(inputs)
      
        # TODO: Update state
        #printOK = True
        printOK = False
        ## self.state = (inputs['light'], self.next_waypoint, deadline)
        self.state = (inputs['light'], self.next_waypoint)
        # self.state = (inputs['light'], inputs['oncoming'], inputs['left'], self.next_waypoint)
        #self.serial += 1
        
        # To see if serial number continues after the agent reaches destination.
        # print self.serial
        if printOK: print "1. current state is:",self.state
        #print self.Qmat

        # TODO: Select action according to your policy

        epsilon = self.epsilon

        if self.state in self.Qmat.keys():
            if printOK: print "   1.a ----------------------------------{} exists".format(self.state)
            action_key_value = self.Qmat[self.state]  # this shows key/value of selected state in Qmat
            # action = max(action_key_value, key = action_key_value.get) # select action of highest probability
            if printOK: print "        Q table for this state: ",action_key_value
            # when multiple maxima exist - choose randomly
            actions_max = {actions:action_value for actions, action_value \
                        in action_key_value.items() if action_value == max(action_key_value.values())}

            action = random.choice(actions_max.keys())
            if printOK: print "      available actions={}".format(actions_max)
            #print "action max={}".format(actions_max)
            #print "action    ={}".format(action)

      	    #print "action+key={}".format(action_key_value)
    	    if printOK: print "         learned_action={}".format(action)
    	    ## action = self.next_waypoint
            if random.random() < epsilon:
                action = random.choice([None, 'forward', 'left', 'right'])
                if printOK: print "         learned_action={} (random)".format(action)
        else:
            if printOK: print "   1.b ----------------------------------{} NEW state".format(self.state)
            self.Qmat[self.state] = {None:0.0, 'forward':0.0, 'left':0.0, 'right':0.0}
            # random action, when landed on a 'new' state
            action = random.choice([None, 'forward', 'left', 'right'])
            # print "action(random)={}".format(action)
            if printOK: print "        random action={}".format(action)
		# Execute action and get reward
        reward = self.env.act(self, action)
        if printOK: print "   Reward for this action={}".format(reward)
        # TODO: Learn policy based on state, action, reward

        # New state definition seems incorrect
        # FIX: New definition of next state: state and waypoint after action was determined above!
        inputs_new = self.env.sense(self)
        
        # This is the key; next_waypoint should be called twice: once above and once here!
        self.next_waypoint = self.planner.next_waypoint()

        # new_state = (inputs_new['light'], inputs_new['oncoming'], inputs_new['left'],action_prime)
        new_state = (inputs_new['light'], self.next_waypoint)
        if printOK: print "2. next state is:",new_state

        if new_state in self.Qmat.keys():
            Q_next = max(self.Qmat[new_state].values())
            if printOK: print "   2.a -----------------------------Q table for NEXT state: ",self.Qmat[new_state]
        else:
            if printOK: print "   2.a -----------------------------Q table for NEXT state: NOT FOUND"
            Q_next = 0.

        if printOK: print "   2.b -----------------------------Q[new state]=", Q_next

        #print "action={},reward = {}".format(action,reward)
        #if action == None:
        #    print "BEFORE:action is NONE: state:{}".format(self.state)
        #    print self.Qmat[self.state]
        
        Qhat = (1.0-self.alpha)*self.Qmat[self.state][action] + self.alpha*(reward+self.gamma*Q_next)
        #Qhat2 =(1.0-self.alpha)*self.Qmat[self.state][action] + (self.alpha*(reward+self.gamma*Q_next))

        #self.Qmat[self.state][action] = (1.0-self.alpha)*self.Qmat[self.state][action] \
        #                              + (self.alpha*(reward+Q_next))              
        # Enhanced Q-learning
        #self.Qmat[self.state][action] = (1.0-self.alpha)*self.Qmat[self.state][action] \
        #                              + (self.alpha*(reward+self.gamma*Q_next))
        
        self.Qmat[self.state][action] = Qhat
        ## print "next_waypoint={},action = {},inputs={}".format(self.next_waypoint, action ,inputs)
        # print "next_waypoint={},A = {}, inputs={},R={}".format(self.next_waypoint, action,inputs ,reward)
        #if not printOK: print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]
        # print self.Qmat
        #if action == None:
        #    print "AFTER: action is NONE: state:{}, Qhat={}, Qhat2={}".format(self.state,Qhat,Qhat2)
        #    print self.Qmat[self.state]
        #else:
        #    print "AFTER: action is else: state:{}, Qhat={}, Qhat2={}".format(self.state,Qhat,Qhat2)
        if printOK: print "3. CONCLUSION"
        if printOK: print "   action is {}, state is {}".format(action,self.state)
        if printOK: print "   Q table for (s,a) is: {}".format(self.Qmat[self.state])
        
        #if reward > 10:
        #    print "************ destination reached *************** "
        #    self.success += 1.0
        #if printOK: print "=========================================================================== end trial"


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # set agent to track
	
	# Now simulate it
    sim = Simulator(e, update_delay=1.0/10000.0)  # reduce update_delay to speed up simulation
    sim.run(n_trials=100)  # press Esc or close pygame window to quit
    
if __name__ == '__main__':
    run()
