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
        blocks_string = ["BlockA", "BlockB", "BlockC", "BlockD", "BlockE", "BlockF", "BlockG", "BlockH", "BlockI", "BlockJ", "BlockK", "BlockL", "BlockM", "BlockN", "BlockO", "BlockP", "BlockQ", "BlockR", "BlockS", "BlockT"]
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
        blocks_string = ["BlockA", "BlockB", "BlockC", "BlockD", "BlockE", "BlockF", "BlockG", "BlockH", "BlockI", "BlockJ", "BlockK", "BlockL", "BlockM", "BlockN", "BlockO", "BlockP", "BlockQ", "BlockR", "BlockS", "BlockT"]
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
        blocks_string = ["BlockA", "BlockB", "BlockC", "BlockD", "BlockE", "BlockF", "BlockG", "BlockH", "BlockI", "BlockJ", "BlockK", "BlockL", "BlockM", "BlockN", "BlockO", "BlockP", "BlockQ", "BlockR", "BlockS", "BlockT"]
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
    