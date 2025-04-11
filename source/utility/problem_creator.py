"""imports from unified planning"""
from os import makedirs
from os.path import exists
from unified_planning.io import PDDLWriter
from unified_planning.model import Problem, Fluent#type: ignore
from unified_planning.shortcuts import (#type: ignore
    BoolType, InstantaneousAction, MinimizeActionCosts, UserType, Object)


class ProblemCreator:
    """ creates basic problems from string names"""

    # error messages
    VARIABLE_NAME_NOT_UNIQUE_ERROR_MESSAGE = "variable names must be unique."
    ACTION_NAME_NOT_UNIQUE_ERROR_MESSAGE = "actions names must be unique."
    PRECONDITION_IS_UNKNOWN_ERROR_MESSAGE = (
        "unknown precondition. preconditions must be in variable list.")
    EFFECT_IS_UNKNOWN_ERROR_MESSAGE = "unknown effect. effect Variables must be in variable list."
    COST_UNKNOWN_ACTION_ERROR_MESSAGE = "cost for unknown action specified."
    GOAL_UNKNOWN_ERROR_MESSAGE = "unknown goal variable. goal variables must be in variable list."
    EMPTY_EFFECT_LIST_MESSAGE = "effect list should not be empty."

    def __init__(
            self,
            variables: list[tuple[str, bool]],
            actions: list[tuple[str, list[str], list[tuple[str, bool]]]],
            goal: list[str]):
        self.problem: Problem = self.create_problem(variables, actions, goal)

    @staticmethod
    def create_problem(
            variables: list[tuple[str, bool]],
            actions: list[tuple[str, list[str], list[tuple[str, bool]]]],
            goal: list[str],
            cost_dict: dict[str, int] | None = None,
            default_cost: int = 1) -> Problem:
        """
        create STRIPS Problems
        @variables list of variables with the initial boolean value (string_name, bool_init_value)
        @actions list of actions action = (string_name, list_precondition, list_of_effects)
        @goal list of goal vars
        """
        # check if no argument given
        if cost_dict is None:
            cost_dict = dict[str, int]()

        # create Problem to work with
        problem: Problem = Problem()

        # remember defined names
        name_to_fluent: dict[str, Fluent] = dict[str, Fluent]()

        # add variables to problem
        for var_name, initial_value in variables:
            # raise error on same variable Name
            if var_name in name_to_fluent:
                raise ValueError(ProblemCreator.VARIABLE_NAME_NOT_UNIQUE_ERROR_MESSAGE
                    + " name: " + var_name)
            new_fluent = Fluent(var_name, BoolType())
            name_to_fluent[var_name] = new_fluent
            problem.add_fluent(new_fluent, default_initial_value=initial_value)

        # remember defined actions
        name_to_action: dict[str, InstantaneousAction] = dict[str, InstantaneousAction]()

        # add actions
        cost_metric_dict = dict[InstantaneousAction, int]()
        for action_name, precondition_list, effect_list in actions:
            # raise error if name for action used more than one time
            if action_name in name_to_action:
                raise ValueError(ProblemCreator.ACTION_NAME_NOT_UNIQUE_ERROR_MESSAGE
                    + " name: " + action_name)
            new_action = InstantaneousAction(action_name)

            # add preconditions
            for precondition_name in precondition_list:
                if precondition_name not in name_to_fluent:
                    raise ValueError(
                        ProblemCreator.PRECONDITION_IS_UNKNOWN_ERROR_MESSAGE
                            + " name: " + precondition_name)
                precondition_fluent = name_to_fluent[precondition_name]
                new_action.add_precondition(precondition_fluent)

            #at least one effect need to be specified
            if len(effect_list) == 0:
                raise ValueError(
                    ProblemCreator.EMPTY_EFFECT_LIST_MESSAGE + " action name: " + action_name)

            # add effects
            for effect_name, effect_result in effect_list:
                if effect_name not in name_to_fluent:
                    raise ValueError(ProblemCreator.EFFECT_IS_UNKNOWN_ERROR_MESSAGE
                        + " name: " + effect_name)
                effect_fluent = name_to_fluent[effect_name]
                new_action.add_effect(effect_fluent, effect_result)

            # add cost metric
            cost_metric_dict[new_action] = (
                cost_dict[action_name]
                if action_name in cost_dict
                else default_cost)

            # add to mapping
            name_to_action[action_name] = new_action

            # add action
            problem.add_action(new_action)

        # add cost metric
        for action_name, _ in cost_dict.items():
            if action_name not in name_to_action:
                raise ValueError(ProblemCreator.COST_UNKNOWN_ACTION_ERROR_MESSAGE
                    + " name: " + action_name)
        problem.add_quality_metric(MinimizeActionCosts(cost_metric_dict, default=default_cost))

        # add goal
        for goal_var_name in goal:
            if goal_var_name not in name_to_fluent:
                raise ValueError(ProblemCreator.GOAL_UNKNOWN_ERROR_MESSAGE
                    + " name: " + goal_var_name)
            goal_var = name_to_fluent[goal_var_name]
            problem.add_goal(goal_var)

        return problem

    @staticmethod
    def create_simple_problems(content_dir: str) -> None:
        "handcrafted problems for evaluation"
        #blocksworld
        
        blocksworld_template = Problem("blocksworld")
        
        #types
        Block = UserType("Block")

        #fluents
        top_free = Fluent("top_free", BoolType(), b=Block)
        on_ground = Fluent("on_ground", BoolType(), b=Block)
        on_top = Fluent("on_top", BoolType(), top=Block, buttom=Block)
        in_hand = Fluent("in_hand", BoolType(), b=Block)
        hand_free = Fluent("hand_free", BoolType())
        blocksworld_template.add_fluent(top_free, default_initial_value=False)
        blocksworld_template.add_fluent(on_ground, default_initial_value=False)
        blocksworld_template.add_fluent(on_top, default_initial_value=False)
        blocksworld_template.add_fluent(in_hand, default_initial_value=False)
        blocksworld_template.add_fluent(hand_free, default_initial_value=True)




        
        #actions

        #take from ground
        take_from_ground = InstantaneousAction("take_from_ground", b=Block)
        take_from_ground_b = take_from_ground.parameter("b")
        #precon
        take_from_ground.add_precondition(hand_free)
        take_from_ground.add_precondition(top_free(take_from_ground_b))
        take_from_ground.add_precondition(on_ground(take_from_ground_b))
        #effects
        take_from_ground.add_effect(hand_free, False)
        take_from_ground.add_effect(top_free(take_from_ground_b), False)
        take_from_ground.add_effect(on_ground(take_from_ground_b), False)
        take_from_ground.add_effect(in_hand(take_from_ground_b), True)
        #add to template
        blocksworld_template.add_action(take_from_ground)

        #take from block
        take_from_blocktower = InstantaneousAction("take_from_blocktower", top=Block, under_top= Block)
        take_from_blocktower_top = take_from_blocktower.parameter("top")
        take_from_blocktower_under_top = take_from_blocktower.parameter("under_top")
        #precon
        take_from_blocktower.add_precondition(hand_free)
        take_from_blocktower.add_precondition(top_free(take_from_blocktower_top))
        take_from_blocktower.add_precondition(on_top(take_from_blocktower_top, take_from_blocktower_under_top))
        #effects
        take_from_blocktower.add_effect(hand_free, False)
        take_from_blocktower.add_effect(top_free(take_from_blocktower_top), False)
        take_from_blocktower.add_effect(top_free(take_from_blocktower_under_top), True)
        take_from_blocktower.add_effect(on_top(take_from_blocktower_top, take_from_blocktower_under_top), False)
        take_from_blocktower.add_effect(in_hand(take_from_blocktower_top), True)
        #add to template
        blocksworld_template.add_action(take_from_blocktower)

        #put on ground
        put_on_ground = InstantaneousAction("put_on_ground", b=Block)
        put_on_ground_b = put_on_ground.parameter("b")
        #precon
        put_on_ground.add_precondition(in_hand(put_on_ground_b))
        #effects
        put_on_ground.add_effect(hand_free, True)
        put_on_ground.add_effect(on_ground(put_on_ground_b), True)
        put_on_ground.add_effect(top_free(put_on_ground_b), True)
        put_on_ground.add_effect(in_hand(put_on_ground_b), False)
        #add to template
        blocksworld_template.add_action(put_on_ground)

        #put on block
        put_on_block = InstantaneousAction("put_on_block", to_put_on=Block, hand_block=Block)
        put_on_block_to_put_on = put_on_block.parameter("to_put_on")
        put_on_block_hand_block = put_on_block.parameter("hand_block")
        #precon
        put_on_block.add_precondition(in_hand(put_on_block_hand_block))
        put_on_block.add_precondition(top_free(put_on_block_to_put_on))
        #effects
        put_on_block.add_effect(hand_free, True)
        put_on_block.add_effect(in_hand(put_on_block_hand_block), False)
        put_on_block.add_effect(top_free(put_on_block_to_put_on), False)
        put_on_block.add_effect(on_top(put_on_block_hand_block, put_on_block_to_put_on), True)
        put_on_block.add_effect(top_free(put_on_block_hand_block), True)
        #add to template
        blocksworld_template.add_action(put_on_block)


        #problem list
        blocksworld_list: list[Problem] = []

        #problem1
        blocksworld1 = blocksworld_template.clone()
        #create Blocks
        blocks_string = ["BlockA", "BlockB", "BlockC"]
        blocks_objects = [Object(block, Block) for block in blocks_string]
        #add objects to problem
        blocksworld1.add_objects(blocks_objects)
        blocksworld1.set_initial_value(hand_free, True)
        #all blocks on the ground
        for block in blocks_objects:
            blocksworld1.set_initial_value(on_ground(block), True)
            blocksworld1.set_initial_value(top_free(block), True)
        #goal all stacked on top A B C
        for index in range(len(blocks_objects) - 1):
            blocksworld1.add_goal(on_top(blocks_objects[index],blocks_objects[index + 1]))
        blocksworld1.add_goal(top_free(blocks_objects[0]))
        blocksworld1.add_goal(on_ground(blocks_objects[-1]))
        blocksworld_list.append(blocksworld1)

        #problem2
        blocksworld2 = blocksworld_template.clone()
        #create Blocks
        blockA = Object("BlockA", Block)
        blockB = Object("BlockB", Block)
        blockC = Object("BlockC", Block)
        blocks_objects = [blockA, blockB, blockC]
        #add objects to problem
        blocksworld2.add_objects(blocks_objects)
        blocksworld2.set_initial_value(hand_free, True)
        #inital values tower stacked the wrong way C B A
        blocksworld2.set_initial_value(top_free(blockC), True)
        blocksworld2.set_initial_value(on_top(blockC,blockB), True)
        blocksworld2.set_initial_value(on_top(blockB,blockA), True)
        blocksworld2.set_initial_value(on_ground(blockA), True)
        #goal all stacked on top A B C
        for index in range(len(blocks_objects) - 1):
            blocksworld2.add_goal(on_top(blocks_objects[index],blocks_objects[index + 1]))
        blocksworld2.add_goal(top_free(blocks_objects[0]))
        blocksworld2.add_goal(on_ground(blocks_objects[-1]))
        blocksworld_list.append(blocksworld2)

        #problem3
        blocksworld3 = blocksworld_template.clone()
        #create Blocks
        blockA = Object("BlockA", Block)
        blockB = Object("BlockB", Block)
        blockC = Object("BlockC", Block)
        blocks_objects = [blockA, blockB, blockC]
        #add objects to problem
        blocksworld3.add_objects(blocks_objects)
        blocksworld3.set_initial_value(hand_free, True)
        #inital values tower stacked the wrong way C B A
        blocksworld3.set_initial_value(top_free(blockC), True)
        blocksworld3.set_initial_value(on_top(blockC,blockB), True)
        blocksworld3.set_initial_value(on_top(blockB,blockA), True)
        blocksworld3.set_initial_value(on_ground(blockA), True)
        #goal all all on ground
        for block in blocks_objects:
            blocksworld3.add_goal(on_ground(block))
            blocksworld3.add_goal(top_free(block))
        
        blocksworld_list.append(blocksworld3)

        #problem4
        blocksworld4 = blocksworld_template.clone()
        #create Blocks
        blocks_string = ["BlockA", "BlockB", "BlockC", "BlockD", "BlockE", "BlockF", "BlockG", "BlockH", "BlockI", "BlockJ"]
        blocks_objects = [Object(block, Block) for block in blocks_string]
        #add objects to problem
        blocksworld4.add_objects(blocks_objects)
        blocksworld4.set_initial_value(hand_free, True)
        #initial values - all on ground
        for block in blocks_objects:
            blocksworld4.set_initial_value(on_ground(block), True)
            blocksworld4.set_initial_value(top_free(block), True)
        #goal all stacked on top A B C
        for index in range(len(blocks_objects) - 1):
            blocksworld4.add_goal(on_top(blocks_objects[index],blocks_objects[index + 1]))
        blocksworld4.add_goal(top_free(blocks_objects[0]))
        blocksworld4.add_goal(on_ground(blocks_objects[-1]))
        blocksworld_list.append(blocksworld4)

        #problem5
        blocksworld5 = blocksworld_template.clone()
        #create Blocks
        blocks_string = ["BlockA", "BlockB", "BlockC", "BlockD", "BlockE", "BlockF", "BlockG", "BlockH", "BlockI", "BlockJ"]
        blocks_objects = [Object(block, Block) for block in blocks_string]
        #add objects to problem
        blocksworld5.add_objects(blocks_objects)
        blocksworld5.set_initial_value(hand_free, True)
        #initial values - tower from behind like C B A
        for index in range(len(blocks_objects) - 1):
             blocksworld5.set_initial_value(on_top(blocks_objects[index + 1], blocks_objects[index]), True)
        blocksworld5.set_initial_value(top_free(blocks_objects[-1]), True)
        blocksworld5.set_initial_value(on_ground(blocks_objects[0]), True)
        #goal all stacked on top A B C
        for index in range(len(blocks_objects) - 1):
            blocksworld5.add_goal(on_top(blocks_objects[index],blocks_objects[index + 1]))
        blocksworld5.add_goal(top_free(blocks_objects[0]))
        blocksworld5.add_goal(on_ground(blocks_objects[-1]))
        blocksworld_list.append(blocksworld5)

        #problem6
        blocksworld6 = blocksworld_template.clone()
        #create Blocks
        blocks_string = ["BlockA", "BlockB", "BlockC", "BlockD", "BlockE", "BlockF", "BlockG", "BlockH", "BlockI", "BlockJ"]
        blocks_objects = [Object(block, Block) for block in blocks_string]
        #add objects to problem
        blocksworld6.add_objects(blocks_objects)
        blocksworld6.set_initial_value(hand_free, True)
        #initial values - tower from behind like C B A
        for index in range(len(blocks_objects) - 1):
             blocksworld6.set_initial_value(on_top(blocks_objects[index + 1], blocks_objects[index]), True)
        blocksworld6.set_initial_value(top_free(blocks_objects[-1]), True)
        blocksworld6.set_initial_value(on_ground(blocks_objects[0]), True)
        #goal all on ground
        for block in blocks_objects:
            blocksworld6.add_goal(on_ground(block))
            blocksworld6.add_goal(top_free(block))
        blocksworld_list.append(blocksworld6)

        #problem7
        blocksworld7 = blocksworld_template.clone()
        #create Blocks
        #blocks_string = ["BlockA", "BlockB", "BlockC", "BlockD", "BlockE", "BlockF", "BlockG", "BlockH", "BlockI", "BlockJ", "BlockK", "BlockL", "BlockM", "BlockN", "BlockO", "BlockP", "BlockQ", "BlockR", "BlockS", "BlockT"]
        blocks_string = ["BlockA", "BlockB"]
        blocks_objects = [Object(block, Block) for block in blocks_string]
        #add objects to problem
        blocksworld7.add_objects(blocks_objects)
        blocksworld7.set_initial_value(hand_free, True)
        #initial values - all on ground
        for block in blocks_objects:
            blocksworld7.set_initial_value(on_ground(block), True)
            blocksworld7.set_initial_value(top_free(block), True)
        #goal all stacked on top A B C
        for index in range(len(blocks_objects) - 1):
            blocksworld7.add_goal(on_top(blocks_objects[index],blocks_objects[index + 1]))
        blocksworld7.add_goal(top_free(blocks_objects[0]))
        blocksworld7.add_goal(on_ground(blocks_objects[-1]))
        blocksworld_list.append(blocksworld7)

        #problem8
        blocksworld8 = blocksworld_template.clone()
        #create Blocks
        #blocks_string = ["BlockA", "BlockB", "BlockC", "BlockD", "BlockE", "BlockF", "BlockG", "BlockH", "BlockI", "BlockJ", "BlockK", "BlockL", "BlockM", "BlockN", "BlockO", "BlockP", "BlockQ", "BlockR", "BlockS", "BlockT"]
        blocks_string = ["BlockA", "BlockB"]
        blocks_objects = [Object(block, Block) for block in blocks_string]
        #add objects to problem
        blocksworld8.add_objects(blocks_objects)
        blocksworld8.set_initial_value(hand_free, True)
        #initial values - tower from behind like C B A
        for index in range(len(blocks_objects) - 1):
             blocksworld8.set_initial_value(on_top(blocks_objects[index + 1], blocks_objects[index]), True)
        blocksworld8.set_initial_value(top_free(blocks_objects[-1]), True)
        blocksworld8.set_initial_value(on_ground(blocks_objects[0]), True)
        #goal all stacked on top A B C
        for index in range(len(blocks_objects) - 1):
            blocksworld8.add_goal(on_top(blocks_objects[index],blocks_objects[index + 1]))
        blocksworld8.add_goal(top_free(blocks_objects[0]))
        blocksworld8.add_goal(on_ground(blocks_objects[-1]))
        blocksworld_list.append(blocksworld8)

        #problem9
        blocksworld9 = blocksworld_template.clone()
        #create Blocks
        #blocks_string = ["BlockA", "BlockB", "BlockC", "BlockD", "BlockE", "BlockF", "BlockG", "BlockH", "BlockI", "BlockJ", "BlockK", "BlockL", "BlockM", "BlockN", "BlockO", "BlockP", "BlockQ", "BlockR", "BlockS", "BlockT"]
        blocks_string = ["BlockA", "BlockB"]
        blocks_objects = [Object(block, Block) for block in blocks_string]
        #add objects to problem
        blocksworld9.add_objects(blocks_objects)
        blocksworld9.set_initial_value(hand_free, True)
        #initial values - tower from behind like C B A
        for index in range(len(blocks_objects) - 1):
             blocksworld9.set_initial_value(on_top(blocks_objects[index + 1], blocks_objects[index]), True)
        blocksworld9.set_initial_value(top_free(blocks_objects[-1]), True)
        blocksworld9.set_initial_value(on_ground(blocks_objects[0]), True)
        #goal all on ground
        for block in blocks_objects:
            blocksworld9.add_goal(on_ground(block))
            blocksworld9.add_goal(top_free(block))
        blocksworld_list.append(blocksworld9)

        #write blocksworld into seperate directory
        count: int = 1
        for blocksworld_problem in blocksworld_list:
            blocksworld_dir = content_dir + "/blocksworld"
            if not exists(blocksworld_dir):
                makedirs(blocksworld_dir)
            subdir_path = blocksworld_dir + "/subdir"+ str(count)
            if not exists(subdir_path):
                makedirs(subdir_path)
            domain_path =  subdir_path + "/" + "domain.pddl"
            problem_path = subdir_path+ "/" + "problem.pddl"
            writer = PDDLWriter(blocksworld_problem)
            writer.write_domain(domain_path)
            writer.write_problem(problem_path)
            count += 1
        

        #pseudo strips
        Obj = UserType("Obj")
        pseudo_strips_problem_list: list[Problem] = []
        pseudo_strips_template = Problem("pseudo_strips")

        #problem1
        pseudo_strips1 = pseudo_strips_template.clone()
        #fluents
        pseudo_strips1_x = Fluent("x",BoolType(), o=Obj)
        pseudo_strips1_y = Fluent("y",BoolType(), o=Obj)
        pseudo_strips1_z = Fluent("z",BoolType(), o=Obj)
        pseudo_strips1_p = Fluent("p",BoolType(), o=Obj)
        pseudo_strips1_q = Fluent("q",BoolType(), o=Obj)
        pseudo_strips1.add_fluent(pseudo_strips1_x, default_initial_value=False)
        pseudo_strips1.add_fluent(pseudo_strips1_y, default_initial_value=False)
        pseudo_strips1.add_fluent(pseudo_strips1_z, default_initial_value=False)
        pseudo_strips1.add_fluent(pseudo_strips1_p, default_initial_value=False)
        pseudo_strips1.add_fluent(pseudo_strips1_q, default_initial_value=False)
        #actions
        pseudo_strips1_a1 = InstantaneousAction("a1", o=Obj)
        pseudo_strips1_a1_o = pseudo_strips1_a1.parameter("o")
        pseudo_strips1_a1.add_precondition(pseudo_strips1_x(pseudo_strips1_a1_o))
        pseudo_strips1_a1.add_precondition(pseudo_strips1_y(pseudo_strips1_a1_o))
        pseudo_strips1_a1.add_effect(pseudo_strips1_p(pseudo_strips1_a1_o), True)
        pseudo_strips1_a1.add_effect(pseudo_strips1_z(pseudo_strips1_a1_o), True)
        pseudo_strips1.add_action(pseudo_strips1_a1)
        pseudo_strips1_a2 = InstantaneousAction("a2", o=Obj)
        pseudo_strips1_a2_o = pseudo_strips1_a2.parameter("o")
        pseudo_strips1_a2.add_precondition(pseudo_strips1_z(pseudo_strips1_a2_o))
        pseudo_strips1_a2.add_effect(pseudo_strips1_q(pseudo_strips1_a2_o), True)
        pseudo_strips1.add_action(pseudo_strips1_a2)
        #initial values
        pseudo_strips1_o1 = Object("o1", Obj)
        pseudo_strips1.add_object(pseudo_strips1_o1)
        pseudo_strips1.set_initial_value(pseudo_strips1_x(pseudo_strips1_o1), True)
        pseudo_strips1.set_initial_value(pseudo_strips1_y(pseudo_strips1_o1), True)
        pseudo_strips1.add_goal(pseudo_strips1_p(pseudo_strips1_o1))
        pseudo_strips1.add_goal(pseudo_strips1_q(pseudo_strips1_o1))
        pseudo_strips_problem_list.append(pseudo_strips1)

        #problem2
        pseudo_strips2 = pseudo_strips_template.clone()
        #fluents
        pseudo_strips2_x = Fluent("x",BoolType(), o=Obj)
        pseudo_strips2_y = Fluent("y",BoolType(), o=Obj)
        pseudo_strips2_z = Fluent("z",BoolType(), o=Obj)
        pseudo_strips2_p = Fluent("p",BoolType(), o=Obj)
        pseudo_strips2_q = Fluent("q",BoolType(), o=Obj)
        pseudo_strips2.add_fluent(pseudo_strips2_x, default_initial_value=False)
        pseudo_strips2.add_fluent(pseudo_strips2_y, default_initial_value=False)
        pseudo_strips2.add_fluent(pseudo_strips2_z, default_initial_value=False)
        pseudo_strips2.add_fluent(pseudo_strips2_p, default_initial_value=False)
        pseudo_strips2.add_fluent(pseudo_strips2_q, default_initial_value=False)
        #action
        pseudo_strips2_a1 = InstantaneousAction("a1", o=Obj)
        pseudo_strips2_a1_o = pseudo_strips2_a1.parameter("o")
        pseudo_strips2_a1.add_precondition(pseudo_strips2_x(pseudo_strips2_a1_o))
        pseudo_strips2_a1.add_precondition(pseudo_strips2_y(pseudo_strips2_a1_o))
        pseudo_strips2_a1.add_effect(pseudo_strips2_z(pseudo_strips2_a1_o), True)
        pseudo_strips2.add_action(pseudo_strips2_a1)
        pseudo_strips2_a2 = InstantaneousAction("a2", o=Obj)
        pseudo_strips2_a2_o = pseudo_strips2_a2.parameter("o")
        pseudo_strips2_a2.add_precondition(pseudo_strips2_z(pseudo_strips2_a2_o))
        pseudo_strips2_a2.add_effect(pseudo_strips2_z(pseudo_strips2_a2_o), False)
        pseudo_strips2_a2.add_effect(pseudo_strips2_p(pseudo_strips2_a2_o), True)
        pseudo_strips2.add_action(pseudo_strips2_a2)
        pseudo_strips2_a3 = InstantaneousAction("a3", o=Obj)
        pseudo_strips2_a3_o = pseudo_strips2_a3.parameter("o")
        pseudo_strips2_a3.add_precondition(pseudo_strips2_z(pseudo_strips2_a3_o))
        pseudo_strips2_a3.add_effect(pseudo_strips2_z(pseudo_strips2_a3_o), False)
        pseudo_strips2_a3.add_effect(pseudo_strips2_q(pseudo_strips2_a3_o), True)
        pseudo_strips2.add_action(pseudo_strips2_a3)
        #initial state
        pseudo_strips2_o1 = Object("o1", Obj)
        pseudo_strips2.add_object(pseudo_strips2_o1)
        pseudo_strips2.set_initial_value(pseudo_strips2_x(pseudo_strips2_o1), True)
        pseudo_strips2.set_initial_value(pseudo_strips2_y(pseudo_strips2_o1), True)
        #goal
        pseudo_strips2.add_goal(pseudo_strips2_p(pseudo_strips2_o1))
        pseudo_strips2.add_goal(pseudo_strips2_q(pseudo_strips2_o1))
        pseudo_strips_problem_list.append(pseudo_strips2)


        count: int = 1
        for pseudo_problem in pseudo_strips_problem_list:
            pseudo_strips_dir = content_dir + "/pseudo_strips"
            if not exists(pseudo_strips_dir):
                makedirs(pseudo_strips_dir)
            subdir_path = pseudo_strips_dir + "/subdir"+ str(count)
            if not exists(subdir_path):
                makedirs(subdir_path)
            domain_path =  subdir_path + "/" + "domain.pddl"
            problem_path = subdir_path+ "/" + "problem.pddl"
            writer = PDDLWriter(pseudo_problem)
            writer.write_domain(domain_path)
            writer.write_problem(problem_path)
            count += 1
    
        #logistics example
        logistics_problem_list: list[Problem] = []
        logistic_problem_template = Problem("logistic-problem")
        #types
        Location = UserType("location")
        Land = UserType("Land")
        Transport = UserType("Transport")
        Goods = UserType("Goods")
        #fluents
        at_location = Fluent("at_location", BoolType(), transport=Transport, location=Location)
        road_from_to = Fluent("road_from_to", BoolType(), road_from=Location, road_to=Location)
        sea_access = Fluent("sea_access", BoolType(), location=Location)
        goods_in_location = Fluent("goods_in_location", BoolType(), goods=Goods, location=Location)
        goods_in_transport = Fluent("goods_in_transport", BoolType(), goods=Goods, transport=Transport)
        location_in_land = Fluent("location_in_land", BoolType(), location=Location, land=Land)
        is_ship = Fluent("is_ship", BoolType(), transport=Transport)
        is_truck = Fluent("is_truck", BoolType(), transport=Transport)
        logistic_problem_template.add_fluent(at_location, default_initial_value=False)
        logistic_problem_template.add_fluent(road_from_to, default_initial_value=False)
        logistic_problem_template.add_fluent(sea_access, default_initial_value=False)
        logistic_problem_template.add_fluent(goods_in_location, default_initial_value=False)
        logistic_problem_template.add_fluent(goods_in_transport, default_initial_value=False)
        logistic_problem_template.add_fluent(location_in_land, default_initial_value=False)
        logistic_problem_template.add_fluent(is_ship, default_initial_value=False)
        logistic_problem_template.add_fluent(is_truck, default_initial_value=False)
        
        #action
        load = InstantaneousAction("load", goods=Goods, transport=Transport, location=Location)
        load_goods = load.parameter("goods")
        load_transport = load.parameter("transport")
        load_location = load.parameter("location")
        load.add_precondition(goods_in_location(load_goods, load_location))
        load.add_precondition(at_location(load_transport, load_location))
        load.add_effect(goods_in_location(load_goods, load_location), False)
        load.add_effect(goods_in_transport(load_goods, load_transport), True)
        logistic_problem_template.add_action(load)
        unload = InstantaneousAction("unload", goods=Goods, transport=Transport, location=Location)
        unload_goods = unload.parameter("goods")
        unload_transport = unload.parameter("transport")
        unload_location = unload.parameter("location")
        unload.add_precondition(goods_in_transport(unload_goods, unload_transport))
        unload.add_precondition(at_location(unload_transport, unload_location))
        unload.add_effect(goods_in_location(unload_goods, unload_location), True)
        unload.add_effect(goods_in_transport(unload_goods, unload_transport), False)
        logistic_problem_template.add_action(unload)
        move_truck = InstantaneousAction("move_truck", transport=Transport, move_from=Location, move_to=Location)
        move_truck_transport=move_truck.parameter("transport")
        move_truck_from=move_truck.parameter("move_from")
        move_truck_to=move_truck.parameter("move_to")
        move_truck.add_precondition(is_truck(move_truck_transport))
        move_truck.add_precondition(at_location(move_truck_transport, move_truck_from))
        move_truck.add_precondition(road_from_to(move_truck_from, move_truck_to))
        move_truck.add_effect(at_location(move_truck_transport, move_truck_from), False)
        move_truck.add_effect(at_location(move_truck_transport, move_truck_to), True)
        logistic_problem_template.add_action(move_truck)
        move_ship = InstantaneousAction("move_ship", transport=Transport, move_from=Location, move_to=Location)
        move_ship_transport=move_ship.parameter("transport")
        move_ship_from=move_ship.parameter("move_from")
        move_ship_to=move_ship.parameter("move_to")
        move_ship.add_precondition(is_ship(move_ship_transport))
        move_ship.add_precondition(sea_access(move_ship_from))
        move_ship.add_precondition(sea_access(move_ship_to))
        move_ship.add_precondition(at_location(move_ship_transport, move_ship_from))
        move_ship.add_effect(at_location(move_ship_transport, move_ship_from), False)
        move_ship.add_effect(at_location(move_ship_transport, move_ship_to), True)
        logistic_problem_template.add_action(move_ship)
        
        #problem1
        logistic_problem1 = logistic_problem_template.clone()
        warehouse_land_1 = Object("warehouse_land_1", Location)
        harbor_land_1 = Object("harbor_land_1", Location)
        warehouse_land_2 = Object("warehouse_land_2", Location)
        harbor_land_2 = Object("harbor_land_2", Location)
        truck_land_1 = Object("truck_land_1", Transport)
        truck_land_2 = Object("truck_land_2", Transport)
        ship = Object("ship", Transport)
        valuable_goods = Object("valuable_goods", Goods)
        logistic_problem1.add_objects([warehouse_land_1, warehouse_land_2, harbor_land_1, harbor_land_2, truck_land_1, truck_land_2, ship, valuable_goods])
        logistic_problem1.set_initial_value(is_truck(truck_land_1), True)
        logistic_problem1.set_initial_value(at_location(truck_land_1, warehouse_land_1), True)
        logistic_problem1.set_initial_value(at_location(truck_land_2, warehouse_land_2), True)
        logistic_problem1.set_initial_value(is_truck(truck_land_2), True)
        logistic_problem1.set_initial_value(is_ship(ship), True)
        logistic_problem1.set_initial_value(at_location(ship, harbor_land_1), True)
        logistic_problem1.set_initial_value(road_from_to(harbor_land_1, warehouse_land_1), True)
        logistic_problem1.set_initial_value(road_from_to(warehouse_land_1, harbor_land_1), True)
        logistic_problem1.set_initial_value(road_from_to(harbor_land_2, warehouse_land_2), True)
        logistic_problem1.set_initial_value(road_from_to(warehouse_land_2, harbor_land_2), True)
        logistic_problem1.set_initial_value(sea_access(harbor_land_1), True)
        logistic_problem1.set_initial_value(sea_access(harbor_land_2), True)
        logistic_problem1.set_initial_value(goods_in_location(valuable_goods, warehouse_land_1), True)
        logistic_problem1.add_goal(goods_in_location(valuable_goods, warehouse_land_2))
        logistics_problem_list.append(logistic_problem1)

        #problem2
        logistic_problem2 = logistic_problem_template.clone()
        warehouse_land_1 = Object("warehouse_land_1", Location)
        harbor_land_1 = Object("harbor_land_1", Location)
        warehouse_land_2 = Object("warehouse_land_2", Location)
        harbor_land_2 = Object("harbor_land_2", Location)
        truck_land_1 = Object("truck_land_1", Transport)
        truck_land_2 = Object("truck_land_2", Transport)
        ship = Object("ship", Transport)
        valuable_goods = Object("valuable_goods", Goods)
        logistic_problem2.add_objects([warehouse_land_1, warehouse_land_2, harbor_land_1, harbor_land_2, truck_land_1, truck_land_2, ship, valuable_goods])
        logistic_problem2.set_initial_value(is_truck(truck_land_1), True)
        logistic_problem2.set_initial_value(at_location(truck_land_1, warehouse_land_1), True)
        logistic_problem2.set_initial_value(at_location(truck_land_2, warehouse_land_2), True)
        logistic_problem2.set_initial_value(is_truck(truck_land_2), True)
        logistic_problem2.set_initial_value(is_ship(ship), True)
        logistic_problem2.set_initial_value(at_location(ship, harbor_land_1), True)
        logistic_problem2.set_initial_value(road_from_to(harbor_land_1, warehouse_land_1), True)
        logistic_problem2.set_initial_value(road_from_to(warehouse_land_1, harbor_land_1), True)
        logistic_problem2.set_initial_value(road_from_to(harbor_land_2, warehouse_land_2), True)
        logistic_problem2.set_initial_value(road_from_to(warehouse_land_2, harbor_land_2), True)
        logistic_problem2.set_initial_value(sea_access(harbor_land_1), True)
        logistic_problem2.set_initial_value(sea_access(harbor_land_2), True)
        logistic_problem2.set_initial_value(goods_in_location(valuable_goods, warehouse_land_1), True)
        logistic_problem2.add_goal(goods_in_location(valuable_goods, harbor_land_1))
        logistics_problem_list.append(logistic_problem2)

        #problem3
        logistic_problem3 = logistic_problem_template.clone()
        warehouse_land_1 = Object("warehouse_land_1", Location)
        harbor_land_1 = Object("harbor_land_1", Location)
        warehouse_land_2 = Object("warehouse_land_2", Location)
        harbor_land_2 = Object("harbor_land_2", Location)
        truck_land_1 = Object("truck_land_1", Transport)
        truck_land_2 = Object("truck_land_2", Transport)
        ship = Object("ship", Transport)
        valuable_goods1 = Object("valuable_goods1", Goods)
        valuable_goods2 = Object("valuable_goods2", Goods)
        logistic_problem3.add_objects([warehouse_land_1, warehouse_land_2, harbor_land_1, harbor_land_2, truck_land_1, truck_land_2, ship, valuable_goods1, valuable_goods2])
        logistic_problem3.set_initial_value(is_truck(truck_land_1), True)
        logistic_problem3.set_initial_value(at_location(truck_land_1, warehouse_land_1), True)
        logistic_problem3.set_initial_value(at_location(truck_land_2, warehouse_land_2), True)
        logistic_problem3.set_initial_value(is_truck(truck_land_2), True)
        logistic_problem3.set_initial_value(is_ship(ship), True)
        logistic_problem3.set_initial_value(at_location(ship, harbor_land_1), True)
        logistic_problem3.set_initial_value(road_from_to(harbor_land_1, warehouse_land_1), True)
        logistic_problem3.set_initial_value(road_from_to(warehouse_land_1, harbor_land_1), True)
        logistic_problem3.set_initial_value(road_from_to(harbor_land_2, warehouse_land_2), True)
        logistic_problem3.set_initial_value(road_from_to(warehouse_land_2, harbor_land_2), True)
        logistic_problem3.set_initial_value(sea_access(harbor_land_1), True)
        logistic_problem3.set_initial_value(sea_access(harbor_land_2), True)
        logistic_problem3.set_initial_value(goods_in_location(valuable_goods1, warehouse_land_1), True)
        logistic_problem3.set_initial_value(goods_in_location(valuable_goods2, warehouse_land_2), True)
        logistic_problem3.add_goal(goods_in_location(valuable_goods1, warehouse_land_2))
        logistic_problem3.add_goal(goods_in_location(valuable_goods2, warehouse_land_1))
        logistics_problem_list.append(logistic_problem3)

        count: int = 1
        for logistics_problem in logistics_problem_list:
            logistic_dir = content_dir + "/logistics"
            if not exists(logistic_dir):
                makedirs(logistic_dir)
            subdir_path = logistic_dir + "/subdir"+ str(count)
            if not exists(subdir_path):
                makedirs(subdir_path)
            domain_path =  subdir_path + "/" + "domain.pddl"
            problem_path = subdir_path+ "/" + "problem.pddl"
            writer = PDDLWriter(logistics_problem)
            writer.write_domain(domain_path)
            writer.write_problem(problem_path)
            count += 1


    
