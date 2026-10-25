"""Question bank for the AI Quiz Arena (DSC401-6, Units I & II).

Every question is a dict with: id, topic, fmt, diff, q, code, kind, options/answer, hint, expl, tags.
kind = "choice" (answer = index into options) | "text" (answer = list of accepted strings)
     | "match" (pairs = [(left, right), ...])
tags: "real_world" (real-world AI scenario) and/or "search" (search / state-space problem).
"""
import re

TOPICS = [
    "Foundations & Applications of AI",
    "Turing Test",
    "Rational & Intelligent Agents",
    "Agents & Environments",
    "Good Behaviour",
    "Nature of Environments",
    "Problems & Problem Spaces",
    "State Space Search",
    "Production Systems",
    "Problem Characteristics",
    "Issues in Search Program Design",
    "BFS",
    "DFS",
    "Iterative Deepening",
    "Hill Climbing",
    "Heuristic & Best-First Search",
    "Constraint Satisfaction (CSP)",
    "Means-End Analysis",
]

AR_OPTIONS = [
    "Both A and R are true, and R is the correct explanation of A",
    "Both A and R are true, but R is NOT the correct explanation of A",
    "A is true, but R is false",
    "A is false, but R is true",
]

FIXED_ORDER_FORMATS = ("True/False", "Assertion-Reason")  # options are never shuffled

QUESTIONS = []


def normalize(s):
    s = re.sub(r"[^\w\s\-]", "", str(s).lower()).strip()
    return re.sub(r"\s+", " ", s)


def _add(**kw):
    kw["id"] = len(QUESTIONS) + 1
    kw.setdefault("code", None)
    kw.setdefault("tags", [])
    QUESTIONS.append(kw)


def mcq(topic, diff, q, options, ans, hint, expl, tags=(), fmt="MCQ", code=None):
    _add(topic=topic, fmt=fmt, diff=diff, q=q, code=code, kind="choice",
         options=list(options), answer=ans, hint=hint, expl=expl, tags=list(tags))


def tf(topic, diff, q, ans, hint, expl, tags=()):
    mcq(topic, diff, q, ["True", "False"], 0 if ans else 1, hint, expl, tags, fmt="True/False")


def ar(topic, diff, a, r, ans, hint, expl, tags=()):
    mcq(topic, diff, f"**Assertion (A):** {a}\n\n**Reason (R):** {r}", AR_OPTIONS, ans,
        hint, expl, tags, fmt="Assertion-Reason")


def fib(topic, diff, q, accepted, hint, expl, tags=(), fmt="Fill in the Blanks", code=None):
    _add(topic=topic, fmt=fmt, diff=diff, q=q, code=code, kind="text",
         answer=[normalize(a) for a in accepted], hint=hint, expl=expl, tags=list(tags))


def match(topic, diff, q, pairs, hint, expl, tags=()):
    _add(topic=topic, fmt="Match the Following", diff=diff, q=q, kind="match",
         pairs=list(pairs), hint=hint, expl=expl, tags=list(tags))


def answer_text(q):
    """Human-readable correct answer."""
    if q["kind"] == "choice":
        return q["options"][q["answer"]]
    if q["kind"] == "text":
        return q["answer"][0]
    return "; ".join(f"{l} → {r}" for l, r in q["pairs"])


RW = ("real_world",)
SR = ("search",)
RW_SR = ("real_world", "search")

# ───────────────────────── Foundations & Applications of AI ─────────────────────────
T = "Foundations & Applications of AI"
mcq(T, "Easy", "Who coined the term 'Artificial Intelligence' for the 1956 Dartmouth workshop?",
    ["Alan Turing", "John McCarthy", "Marvin Minsky", "Herbert Simon"], 1,
    "He also created the LISP language.",
    "John McCarthy proposed the term 'Artificial Intelligence' in the 1955 proposal for the 1956 Dartmouth workshop.")
tf(T, "Easy", "A chess program that can do nothing except play chess is an example of Narrow (Weak) AI.", True,
   "Think: one task only vs. human-level general ability.",
   "Narrow AI is built for a specific task. General AI (human-level across tasks) does not exist yet.")
mcq(T, "Medium", "A phone's voice assistant converts your speech to text, understands the request and replies in "
    "natural language. Which AI areas are mainly involved?",
    ["Speech recognition + Natural Language Processing", "Computer vision + Robotics",
     "Expert systems + Game playing", "Genetic algorithms + Fuzzy logic"], 0,
    "Input is audio, output is language.",
    "Voice assistants combine automatic speech recognition (ASR) with NLP for understanding and generation.",
    tags=RW, fmt="Scenario-based")
mcq(T, "Medium", "A hospital uses software that scans chest X-rays and flags probable pneumonia. "
    "Which AI application area is this?",
    ["Natural Language Generation", "Computer Vision (medical image analysis)", "Game Playing",
     "Automated Theorem Proving"], 1,
    "The input is an image.",
    "Analysing medical images is a computer-vision task, typically solved with deep learning.",
    tags=RW, fmt="Scenario-based")
fib(T, "Easy", "The four approaches to AI are: thinking humanly, thinking rationally, acting humanly and acting ______.",
    ["rationally"], "The 'rational agent' approach.",
    "Acting rationally (the rational-agent approach) is the most widely used definition of AI today.")

# ───────────────────────── Turing Test ─────────────────────────
T = "Turing Test"
mcq(T, "Easy", "Turing proposed the 'Imitation Game' in which 1950 paper?",
    ["Computing Machinery and Intelligence", "Steps Toward Artificial Intelligence",
     "A Logical Calculus of the Ideas Immanent in Nervous Activity", "Programs with Common Sense"], 0,
    "The title asks 'Can machines think?'",
    "Turing's 1950 paper 'Computing Machinery and Intelligence' introduced the test.")
tf(T, "Medium", "In the Turing Test the human interrogator can see and touch the machine to judge its intelligence.",
   False, "The test is text-based.",
   "The interrogator communicates only through text so that physical appearance does not influence the judgement.")
fib(T, "Hard", "The 'Total Turing Test' adds computer vision and ______ (to manipulate objects and move about).",
    ["robotics"], "Think of the body of the machine.",
    "The Total Turing Test requires perception (vision) and physical action (robotics) in addition to language.")
ar(T, "Medium", "To pass the standard Turing Test a machine needs natural language processing.",
   "The interrogator communicates with the machine only through typed text.", 0,
   "Text-only channel -> language ability is essential.",
   "Because the whole test is a text conversation, the machine must understand and generate natural language.")

# ───────────────────────── Rational & Intelligent Agents ─────────────────────────
T = "Rational & Intelligent Agents"
mcq(T, "Easy", "An agent perceives its environment through ______ and acts upon it through ______.",
    ["sensors; actuators", "actuators; sensors", "rules; goals", "memory; CPU"], 0,
    "Perception in, action out.", "This is the standard definition of an agent.")
mcq(T, "Medium", "A rational agent selects the action expected to maximise its ______.",
    ["performance measure", "speed of execution", "number of rules", "memory usage"], 0,
    "What do we use to judge success?",
    "Rationality is about maximising the expected value of the performance measure, given the percept sequence "
    "and built-in knowledge.")
tf(T, "Medium", "A rational agent is the same thing as an omniscient agent.", False,
   "Does a rational agent know the actual outcome of its actions?",
   "An omniscient agent knows actual outcomes; a rational agent only maximises EXPECTED performance with what it knows.")
match(T, "Medium", "Match each agent type with its key idea.",
      [("Simple reflex agent", "Acts on the current percept using condition-action rules"),
       ("Model-based reflex agent", "Maintains an internal state of the unseen world"),
       ("Goal-based agent", "Chooses actions that achieve an explicit goal"),
       ("Utility-based agent", "Maximises a measure of 'happiness' among competing outcomes")],
      "Move from least to most sophisticated.",
      "Simple reflex -> model-based -> goal-based -> utility-based, each adding more reasoning ability.")
mcq(T, "Hard", "Which component of a learning agent suggests exploratory actions leading to new, informative experiences?",
    ["Problem generator", "Critic", "Performance element", "Learning element"], 0,
    "It 'generates problems' to try out.",
    "The problem generator proposes exploratory actions; the critic gives feedback; the learning element improves "
    "the performance element.")
mcq(T, "Hard", "Which agent type is best when goals conflict or can be achieved with different degrees of certainty?",
    ["Utility-based agent", "Simple reflex agent", "Model-based reflex agent", "Table-driven agent"], 0,
    "You need a way to trade off outcomes.",
    "A utility function maps states to a degree of preference, allowing trade-offs between conflicting goals.")

# ───────────────────────── Agents & Environments ─────────────────────────
T = "Agents & Environments"
fib(T, "Easy", "PEAS stands for Performance measure, Environment, Actuators and ______.",
    ["sensors"], "What the agent perceives with.", "PEAS = Performance, Environment, Actuators, Sensors.")
mcq(T, "Medium", "In the PEAS description of an automated taxi, which item is an ACTUATOR?",
    ["Steering, accelerator and brake", "Camera", "GPS", "Speedometer"], 0,
    "Actuators DO things; sensors MEASURE things.",
    "Steering, accelerator, brake, horn and display are actuators. Camera, GPS and speedometer are sensors.",
    tags=RW)
ar(T, "Hard", "A simple reflex agent can fail in a partially observable environment.",
   "It decides using only the current percept and keeps no internal state.", 0,
   "What is missing if you cannot see everything?",
   "Without memory of past percepts it cannot infer hidden parts of the state, so it may loop or act wrongly.")
mcq(T, "Medium", "A robot vacuum turns whenever its bumper sensor hits a wall, with no memory of the room. "
    "Which agent type is it?",
    ["Simple reflex agent", "Utility-based agent", "Learning agent", "Goal-based agent"], 0,
    "Condition -> action, nothing more.",
    "'If bumper pressed then turn' is a condition-action rule on the current percept: a simple reflex agent.",
    tags=RW, fmt="Scenario-based")

# ───────────────────────── Good Behaviour ─────────────────────────
T = "Good Behaviour"
tf(T, "Medium", "A performance measure should reflect what we want in the environment, not how we think the agent should behave.",
   True, "Measure outcomes, not methods.",
   "Design the measure around desired environment states; otherwise the agent may satisfy the letter, not the intent.")
mcq(T, "Hard", "A vacuum agent is rewarded for the amount of dirt collected. It learns to dump dirt and re-clean it. "
    "What does this illustrate?",
    ["A badly designed performance measure", "An omniscient agent", "A partially observable environment",
     "A deterministic environment"], 0,
    "The reward is being gamed.",
    "Rewarding dirt collected (instead of a clean floor) is a flawed performance measure and encourages the agent to cheat.",
    fmt="Scenario-based")

# ───────────────────────── Nature of Environments ─────────────────────────
T = "Nature of Environments"
mcq(T, "Easy", "An environment is fully observable if...",
    ["the agent's sensors give access to the complete state at each point in time",
     "the environment never changes", "there is only one agent", "the next state is random"], 0,
    "Think: nothing hidden from the agent.",
    "Fully observable means sensors detect every aspect relevant to the choice of action.")
match(T, "Medium", "Match each task with its environment properties.",
      [("Crossword puzzle", "Static and deterministic"),
       ("Poker", "Partially observable and stochastic"),
       ("Taxi driving", "Dynamic and continuous"),
       ("Inspecting parts on a conveyor (one at a time)", "Episodic")],
      "Ask: can it change while the agent thinks? Are other cards hidden?",
      "Crosswords do not change; poker hides cards and has chance; driving is continuous and changes in real time; "
      "part inspection decisions are independent episodes.")
mcq(T, "Medium", "A self-driving car in busy city traffic operates in which kind of environment?",
    ["Dynamic, partially observable and stochastic", "Static and fully observable", "Episodic and discrete",
     "Deterministic and static"], 0,
    "Other cars and pedestrians move unpredictably.",
    "Traffic changes while the car decides (dynamic), sensors miss things (partially observable) and outcomes are uncertain.",
    tags=RW, fmt="Scenario-based")
mcq(T, "Hard", "Which task is best described as EPISODIC?",
    ["Classifying each incoming e-mail as spam or not spam", "Playing a full game of chess", "Driving a taxi",
     "Playing tic-tac-toe"], 0,
    "Does one decision affect the next?",
    "Each e-mail is classified independently of earlier ones; in chess, taxi driving and tic-tac-toe current "
    "decisions affect future ones (sequential).", tags=RW)
fib(T, "Medium", "An environment in which several agents interact (cooperatively or competitively) is called a ______-agent environment.",
    ["multi", "multiple", "multiagent", "multi-agent", "multi agent"], "The opposite of single.",
    "Chess (competitive) and taxi driving (partly cooperative) are multi-agent environments.")

# ───────────────────────── Problems & Problem Spaces ─────────────────────────
T = "Problems & Problem Spaces"
mcq(T, "Easy", "Which of these is NOT a component of a well-defined problem?",
    ["Initial state", "Goal test", "Path cost", "Programming language used to code the solution"], 3,
    "Think about the formal definition.",
    "A well-defined problem has an initial state, actions/operators, a goal test and a path cost.")
fib(T, "Medium", "The set of all states reachable from the initial state by any sequence of actions is called the state ______.",
    ["space"], "Where the search takes place.", "The state space is a graph of states (nodes) and actions (edges).")

# ───────────────────────── State Space Search ─────────────────────────
T = "State Space Search"
mcq(T, "Medium", "In the 8-puzzle, how many moves are possible when the blank is in the CENTRE square?",
    ["2", "3", "4", "8"], 2, "The blank can slide up, down, left or right.",
    "From the centre the blank can move in all four directions (corners have 2, edges have 3).",
    tags=SR, fmt="Problem-Solving")
mcq(T, "Hard", "There are 9! = 362,880 arrangements of the 8-puzzle. How many are reachable from any one start state?",
    ["181,440", "362,880", "40,320", "9"], 0, "Exactly half of all arrangements.",
    "Parity splits the arrangements into two unreachable halves, so only 9!/2 = 181,440 are reachable.",
    tags=SR, fmt="Problem-Solving")
mcq(T, "Medium", "4 L and 3 L jugs are empty; state = (litres in 4 L jug, litres in 3 L jug). "
    "Fill the 3 L jug, then pour all of it into the 4 L jug. New state?",
    ["(3, 0)", "(0, 3)", "(3, 3)", "(4, 3)"], 0, "Fill gives (0, 3). Then move the water across.",
    "(0,0) -> fill 3 L -> (0,3) -> pour into 4 L jug (it has room) -> (3,0).",
    tags=SR, fmt="Problem-Solving")

# ───────────────────────── Production Systems ─────────────────────────
T = "Production Systems"
mcq(T, "Medium", "Which of these is NOT a component of a production system?",
    ["A set of production rules", "A global database (working memory)", "A control strategy",
     "A gradient-descent optimiser"], 3, "Rules + data + control.",
    "A production system = production rules + global database + control strategy (rule applier).")
tf(T, "Hard", "In a commutative production system, the order in which a set of applicable rules is applied does not change the resulting state.",
   True, "'Commutative' like a + b = b + a.",
   "Commutativity means rule order is irrelevant to the final state, so no backtracking is needed.")

# ───────────────────────── Problem Characteristics ─────────────────────────
T = "Problem Characteristics"
match(T, "Medium", "Match each problem with its characteristic.",
      [("Theorem proving", "Ignorable (steps can be ignored)"),
       ("8-puzzle", "Recoverable (steps can be undone)"),
       ("Chess", "Irrecoverable (moves cannot be undone)"),
       ("Symbolic integration", "Decomposable into independent sub-problems")],
      "Can you take a move back?",
      "Rich & Knight: theorem proving is ignorable, 8-puzzle recoverable, chess irrecoverable.")
ar(T, "Medium", "Chess is an irrecoverable problem.", "A move once made cannot be taken back.", 0,
   "Think of the 'touch-move' rule.", "Irrecoverable = steps cannot be undone, which is true of chess moves.")
mcq(T, "Hard", "Which problem needs only a final STATE as its solution rather than a PATH of steps?",
    ["Water-jug problem", "8-puzzle", "Interpreting the meaning of a sentence", "Travelling salesman problem"], 2,
    "Do we care HOW we got to the interpretation?",
    "For language interpretation only the final meaning matters; the other problems need the sequence of moves/route.")

# ───────────────────────── Issues in Search Program Design ─────────────────────────
T = "Issues in Search Program Design"
mcq(T, "Medium", "Which is a major issue in designing a search program?",
    ["Whether to search forward from the start or backward from the goal", "Choosing the font of the output",
     "Choosing the colour of nodes", "Choosing the operating system"], 0,
    "Direction of search.",
    "Key issues: direction of search, rule selection, tree vs graph representation, node matching, heuristics.")
tf(T, "Medium", "Representing the search space as a graph (not a tree) helps avoid re-expanding repeated states.", True,
   "Same state reached by two paths.",
   "A graph search recognises repeated states and avoids the wasted work (and loops) of a tree search.")
fib(T, "Hard", "The rapid growth in the number of states as search depth increases is called combinatorial ______.",
    ["explosion"], "It blows up!", "This is why heuristics and pruning are essential in search.")

# ───────────────────────── BFS ─────────────────────────
T = "BFS"
mcq(T, "Easy", "Which data structure does Breadth-First Search use for its frontier?",
    ["Queue (FIFO)", "Stack (LIFO)", "Priority queue ordered by h(n)", "Hash table"], 0,
    "First in, first out.", "BFS expands the shallowest node first, which a FIFO queue naturally gives.")
tf(T, "Medium", "BFS is complete if the branching factor is finite.", True, "It will reach every depth eventually.",
   "BFS explores level by level, so it finds a goal at finite depth if one exists.")
mcq(T, "Medium", "With branching factor b and shallowest goal at depth d, the time complexity of BFS is...",
    ["O(b^d)", "O(b + d)", "O(d)", "O(b x d)"], 0, "Exponential in depth.",
    "BFS generates 1 + b + b^2 + ... + b^d nodes, i.e. O(b^d).")
fib(T, "Medium", "How many nodes are there in a complete binary tree of depth 3 (root at depth 0)?",
    ["15"], "1 + 2 + 4 + 8", "1 + 2 + 4 + 8 = 15 nodes.", tags=SR, fmt="Problem-Solving")
mcq(T, "Medium", "A web crawler must find the page containing a keyword that is reachable in the fewest clicks from the home page. "
    "Which search strategy fits best?",
    ["Breadth-First Search", "Depth-First Search", "Hill Climbing", "Means-End Analysis"], 0,
    "Fewest clicks = shallowest solution.",
    "BFS finds the shallowest goal first, so it minimises the number of clicks (steps).",
    tags=RW_SR, fmt="Scenario-based")

# ───────────────────────── DFS ─────────────────────────
T = "DFS"
mcq(T, "Medium", "Visiting children left-to-right, what is the DFS (pre-order) visiting sequence of this tree?",
    ["A B D E C F G", "A B C D E F G", "A C G F B E D", "D E B F G C A"], 0,
    "Go as deep as possible before backing up.",
    "DFS: A, go to B, go to D (leaf), back to E, back up to C, then F, G. (A B C D E F G is BFS.)",
    tags=SR, fmt="Problem-Solving",
    code="        A\n       / \\\n      B   C\n     / \\ / \\\n    D  E F   G")
mcq(T, "Hard", "With branching factor b and maximum depth m, the space complexity of DFS is...",
    ["O(bm)", "O(b^d)", "O(b^m)", "O(m!)"], 0, "Only one path (plus siblings) is stored.",
    "DFS stores a single path from the root plus unexpanded siblings, giving linear space O(bm).")
ar(T, "Medium", "DFS needs far less memory than BFS.",
   "DFS stores only the current path and the unexpanded siblings along it.", 0,
   "Compare how much each keeps in memory.",
   "BFS must hold an entire level (exponential), while DFS holds one path (linear).")
tf(T, "Medium", "DFS is guaranteed to find the shallowest (optimal) goal.", False, "It might dive into a deep branch first.",
   "DFS may find a deep goal before a shallow one, and can get stuck in infinite branches; it is neither optimal nor complete in general.")

# ───────────────────────── Iterative Deepening ─────────────────────────
T = "Iterative Deepening"
mcq(T, "Medium", "Iterative Deepening Search combines...",
    ["BFS's completeness and optimality with DFS's low memory use", "BFS's memory use with DFS's speed",
     "Hill climbing with BFS", "Heuristics with CSP"], 0, "Best of both worlds.",
    "IDS repeatedly runs depth-limited DFS with increasing limits: complete, optimal (unit cost) and O(bd) memory.")
tf(T, "Hard", "Because IDS regenerates upper-level nodes repeatedly, its asymptotic time complexity is much worse than BFS.",
   False, "Most nodes are at the deepest level.",
   "The repeated work is small because most nodes lie in the last level; IDS is still O(b^d).")
fib(T, "Medium", "In ______-limited search, DFS is cut off at a predefined depth l to avoid infinite paths.",
    ["depth"], "The limit is on how far down you go.", "Depth-limited search treats nodes at depth l as having no successors.")
mcq(T, "Hard", "A chess engine on a phone has tight memory and a time limit, and must always have a best-so-far move ready. "
    "Which strategy suits it best?",
    ["Iterative deepening", "Pure BFS storing the whole tree", "Hill climbing with no restarts", "Random guessing"], 0,
    "Anytime behaviour + low memory.",
    "Iterative deepening uses little memory and after each completed depth gives a valid best move, so it can stop anytime.",
    tags=RW_SR, fmt="Scenario-based")

# ───────────────────────── Hill Climbing ─────────────────────────
T = "Hill Climbing"
tf(T, "Easy", "Hill climbing keeps only the current state and does not backtrack.", True, "It has no memory of previous states.",
   "Hill climbing is a local search that moves to a better neighbour and stops when none exists.")
match(T, "Medium", "Match each hill-climbing variant with its behaviour.",
      [("Simple hill climbing", "Moves to the FIRST better neighbour found"),
       ("Steepest-ascent hill climbing", "Examines ALL neighbours and picks the best"),
       ("Stochastic hill climbing", "Picks randomly among the uphill moves"),
       ("Random-restart hill climbing", "Restarts from random states to escape local maxima")],
      "Think about how many neighbours are checked.",
      "These variants differ in how the next move is chosen; random restart tackles local maxima.")
mcq(T, "Medium", "A flat region of the landscape where all neighbouring states have the same value is called a...",
    ["Plateau", "Ridge", "Peak", "Valley"], 0, "Flat = ?",
    "Plateaus give hill climbing no direction. Ridges are narrow slopes; local maxima are peaks lower than the global one.")
ar(T, "Hard", "Random-restart hill climbing is more likely to reach the global maximum than simple hill climbing.",
   "Each restart begins from a different random initial state.", 0, "Different starting points -> different hills.",
   "With enough restarts one run is likely to begin on the slope of the global maximum.")
mcq(T, "Medium", "A delivery app tweaks the current route by swapping two stops whenever that shortens the total distance, "
    "and repeats until no swap helps. Which technique is this?",
    ["Hill climbing (local search)", "Breadth-first search", "Means-end analysis", "Minimax"], 0,
    "Improve the current solution step by step.",
    "Repeatedly accepting better neighbouring routes is hill climbing (e.g. 2-opt); it may stop at a local optimum.",
    tags=RW, fmt="Scenario-based")

# ───────────────────────── Heuristic & Best-First Search ─────────────────────────
T = "Heuristic & Best-First Search"
mcq(T, "Easy", "A heuristic function h(n) estimates...",
    ["the cost from node n to the nearest goal", "the cost from the start to node n", "the depth of node n",
     "the number of children of node n"], 0, "It looks ahead.",
    "h(n) is the estimated remaining cost to reach a goal; g(n) is the cost so far.")
tf(T, "Medium", "Greedy Best-First Search expands the node with the smallest f(n) = h(n).", True, "It only looks at the estimate.",
   "Greedy search is fast but neither optimal nor complete in general since it ignores the cost so far.")
mcq(T, "Medium", "The evaluation function of A* search is...",
    ["f(n) = g(n) + h(n)", "f(n) = h(n)", "f(n) = g(n)", "f(n) = g(n) - h(n)"], 0, "Cost so far + estimated cost to go.",
    "A* balances the actual cost g(n) and estimated remaining cost h(n).")
mcq(T, "Hard", "A* (tree search) is guaranteed to return an optimal solution when h(n) is...",
    ["admissible (never overestimates the true cost)", "always larger than the true cost", "randomly generated",
     "equal to g(n)"], 0, "'Optimistic'.",
    "An admissible heuristic never overestimates, so A* will not skip over the cheapest path.")
fib(T, "Hard", "For the start state below, what is the total Manhattan distance heuristic (blank not counted) to reach the goal?",
    ["2"], "Only two tiles are out of place.",
    "Tile 5 is 1 move from its goal square and tile 8 is 1 move: 1 + 1 = 2.",
    tags=SR, fmt="Problem-Solving",
    code="Start     Goal\n1 2 3     1 2 3\n4 _ 6     4 5 6\n7 5 8     7 8 _")
mcq(T, "Medium", "A navigation app finds the shortest road route using straight-line distance to the destination as an estimate. "
    "Which algorithm is this?",
    ["A* search", "Depth-first search", "Hill climbing without restarts", "Depth-limited search"], 0,
    "g(n) + straight-line h(n).",
    "Straight-line distance never overestimates road distance (admissible), so A* gives optimal routes.",
    tags=RW_SR, fmt="Scenario-based")

# ───────────────────────── Constraint Satisfaction (CSP) ─────────────────────────
T = "Constraint Satisfaction (CSP)"
mcq(T, "Easy", "A Constraint Satisfaction Problem is defined by...",
    ["Variables, domains and constraints", "States, actions and rewards", "Rules, facts and goals",
     "Nodes, edges and weights"], 0, "V, D, C.", "A CSP has a set of variables, a domain of values for each and constraints.")
mcq(T, "Medium", "In exam timetabling modelled as a CSP, what is a typical constraint?",
    ["Two exams that share a student cannot be in the same time slot", "All exams must be on the same day",
     "Every exam must have a different room size", "Students must write exams alphabetically"], 0,
    "A student cannot be in two places at once.",
    "Variables = exams, domain = time slots, constraint = conflicting exams get different slots (like graph colouring).",
    tags=RW, fmt="Scenario-based")
fib(T, "Medium", "In backtracking CSP search, ______ checking removes inconsistent values from the domains of unassigned neighbours after each assignment.",
    ["forward"], "It looks ahead one step.", "Forward checking detects failure early by pruning neighbouring domains.")
mcq(T, "Hard", "The Minimum Remaining Values (MRV) heuristic chooses...",
    ["the variable with the fewest legal values left", "the value that rules out the fewest values in neighbours",
     "the variable involved in the most constraints", "a random variable"], 0,
    "'Fail-first' heuristic.",
    "MRV picks the most constrained variable. Option 2 is Least-Constraining-Value; option 3 is the Degree heuristic.")
mcq(T, "Medium", "Three mutually adjacent regions must all get different colours. Minimum colours needed?",
    ["2", "3", "4", "1"], 1, "Each region touches the other two.",
    "Every pair is adjacent so all three need distinct colours: 3.", fmt="Problem-Solving", tags=SR)
fib(T, "Hard", "In the cryptarithmetic puzzle SEND + MORE = MONEY, the digit M equals ______.",
    ["1"], "The carry from adding two 4-digit numbers is at most 1.",
    "The sum of two 4-digit numbers is below 20,000, so the leading digit M of MONEY must be 1.",
    fmt="Problem-Solving")
ar(T, "Medium", "Sudoku is a constraint satisfaction problem.",
   "Each cell is a variable with domain {1..9}, and every row, column and box must be all-different.", 0,
   "Identify variables, domains, constraints.", "That variable/domain/constraint description is exactly a CSP.")

# ───────────────────────── Means-End Analysis ─────────────────────────
T = "Means-End Analysis"
mcq(T, "Medium", "Means-End Analysis works by...",
    ["repeatedly reducing the difference between the current state and the goal state",
     "expanding nodes level by level", "choosing random moves", "assigning colours to variables"], 0,
    "Find the difference, pick an operator that reduces it.",
    "MEA identifies the difference between current and goal states and selects operators that reduce it.")
tf(T, "Medium", "Newell and Simon's General Problem Solver (GPS) used Means-End Analysis.", True, "1950s-60s AI program.",
   "GPS was the classic implementation of means-end analysis.")
mcq(T, "Hard", "In MEA, if the chosen operator cannot be applied yet, the system...",
    ["sets up a sub-goal to reach a state where the operator is applicable", "discards the operator forever",
     "restarts the whole search", "switches to DFS"], 0, "Recursive sub-goaling.",
    "MEA creates a sub-problem: get to a state in which the operator's preconditions hold, then apply it.")
mcq(T, "Medium", "A warehouse robot must deliver a parcel to a room behind a closed door. It first sets the sub-goal "
    "'open the door' and then plans the delivery. Which technique is this?",
    ["Means-End Analysis", "Hill climbing with random restart", "Constraint propagation", "Breadth-first search"], 0,
    "Sub-goals to remove the difference.",
    "Creating sub-goals to remove obstacles between the current state and the goal is means-end analysis.",
    tags=RW, fmt="Scenario-based")

# ── sanity checks ──
assert all(q["topic"] in TOPICS for q in QUESTIONS), "unknown topic"
assert all(q["kind"] != "choice" or 0 <= q["answer"] < len(q["options"]) for q in QUESTIONS)
