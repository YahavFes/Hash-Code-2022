import argparse
import networkx as nx
from copy import deepcopy


class Contributor:
    def __init__(self, contributor_name, skills):
        self.contributor_name = contributor_name
        self.skills = skills  # Dictionary that map name of skill to its skill number
        self.is_available = True  # indication whether the contributor is currently working on project
        self.available_on = 0


class Project:
    def __init__(self, project_name, num_of_days, score, best_before_day, requirements):
        self.project_name = project_name
        self.num_of_days = num_of_days
        self.score = score
        self.best_before_day = best_before_day
        self.requirements = requirements  # Dictionary that map the skill name to its skill number


class Repository:
    def __init__(self, contributors, projects):
        self.contributors = contributors
        self.projects = projects


curr_day = 0


def sort_projects(projects):
    projects.sort(lambda project: calc_profit(project))


def calc_profit(project):
    penalty = 0 if curr_day + project.num_of_days <= project.best_before_day else \
        curr_day + project.num_of_days - project.best_before_day
    return max(project.score - penalty, 0) / (project.num_of_days * len(project.requirements))


# the projects have to be sorted
# if None returned then oops!
def project_bin_search(workers, projects, minimumz):
    max_ind = len(projects)
    min_ind = minimumz
    while (min_ind + 1 < max_ind):
        print("**********************")
        mid = (max_ind + min_ind) // 2
        max_match = get_max_weight_matching(projects[-mid:], workers)
        if max_match == None:
            max_ind = mid
        else:
            min_ind = mid
    print(curr_day)
    max_match = get_max_weight_matching(projects[-max_ind:], workers)
    if max_match != None:
        return max_ind
    return min_ind


def decide_projects(workers, projects, minz):
    best = len(projects)
    res = project_bin_search(workers, projects, minz)
    if (best <= res):
        return get_max_weight_matching(projects, workers)
    else:
        print(len(projects))
        projects.pop(len(projects) - res - 1)
        print(len(projects))
        return decide_projects(workers, projects, res)


def parse(filename):
    with open(filename) as fp:
        # Parse the first line
        line = fp.readline()
        num_of_contributors = int(line.split(" ")[0])
        num_of_projects = int(line.split(" ")[1])

        # Parse the contributors
        contributors = []
        # Iterating over the contributors
        for i in range(num_of_contributors):
            skills = {}
            line = fp.readline()
            # The name of the contributor and its num of skills
            contributor_name = line.split(" ")[0]
            num_of_skills = int(line.split(" ")[1])
            for j in range(num_of_skills):
                line = fp.readline()
                skill_name = line.split(" ")[0]
                skill_num = int(line.split(" ")[1])
                skills[skill_name] = skill_num
            curr_contributor = Contributor(contributor_name, skills)
            contributors.append(curr_contributor)

        # Parse the projects
        projects = []
        # Iterating over the projects
        for i in range(num_of_projects):
            line = fp.readline()
            project_name = line.split(" ")[0]
            num_of_days = int(line.split(" ")[1])
            score = line.split(" ")[2]
            best_before_day = int(line.split(" ")[3])
            num_of_requirements = int(line.split(" ")[4])
            requirements = []
            for j in range(num_of_requirements):
                line = fp.readline()
                skill_name = line.split(" ")[0]
                skill_num = int(line.split(" ")[1])
                requirements.append((skill_name, skill_num))
            curr_project = Project(project_name, num_of_days, score, best_before_day, requirements)
            projects.append(curr_project)
        repository = Repository(contributors, projects)

    return repository


def get_max_weight_matching(projects, contributors):
    graph = nx.Graph()

    for contributor in contributors:
        graph.add_node(contributor.contributor_name)

    num_of_conditions = 0
    for project in projects:
        for element in project.requirements:
            project_skill_name = element[0]
            node_name = "{}_{}".format(project.project_name, project_skill_name)
            graph.add_node(node_name)
            for contributor in contributors:
                if contributor.is_available:
                    if project_skill_name in contributor.skills:
                        weight = 100000000000
                        if contributor.skills[project_skill_name] == element[1]:
                            weight += 1
                        graph.add_edge(contributor.contributor_name, node_name, weight=weight)
            num_of_conditions += 1

    max_weight_matching = nx.max_weight_matching(graph)
    if len(max_weight_matching) != num_of_conditions:
        return None
    else:
        return max_weight_matching


def convert_edges_to_result(edges, original_repository):
    if edges is None:
        return []

    projects = original_repository.projects
    result = []
    for project in projects:
        list_of_contributors = []
        for element in project.requirements:
            skill_name = element[0]
            contributor_name = ''
            for edge in edges:
                first_node, second_node = edge
                if '_' in first_node:
                    first_node, second_node = second_node, first_node
                if project.project_name == second_node.split('_')[0] and skill_name == second_node.split('_')[1]:
                    contributor_name = first_node
                    break
            if contributor_name != '':
                list_of_contributors.append(contributor_name)
        if len(list_of_contributors) > 0:
            result.append((project.project_name, list_of_contributors))

    return result


def remove_project_from_repository(repository, project_name):
    projects = deepcopy(repository.projects)
    for index, project in enumerate(projects):
        if project.project_name == project_name:
            projects.pop(index)

    repository.projects = projects


def create_output(result):
    with open("output.txt", 'w') as fp:
        fp.write(str(len(result)) + '\n') # Write the number of planned projects
        for element in result:
            project_name, list_of_contributors = element
            fp.write(project_name + "\n")
            fp.write(" ".join(list_of_contributors) + "\n")


def find_project_in_repo(repository, proj):
    for p in repository.projects:
        if p.project_name == proj:
            return p
    return None


def wake_up_workers(repository):
    global curr_day
    for worker in repository.contributors:
        if worker.available_on == curr_day:
            worker.is_available = True


def get_contributor_by_name(repository, name):
    for contributor in repository.contributors:
        if contributor.contributor_name == name:
            return contributor


def main(filename):
    global curr_day
    curr_day = 0
    original_repository = parse(filename)
    repository = parse(filename)
    full_answer = []
    for i in range(1000):
        wake_up_workers(repository)
        result = convert_edges_to_result(decide_projects(repository.contributors, repository.projects, 0), original_repository)
        for j in result:
            for person in j[1]:
                get_contributor_by_name(repository, person).is_available = False
                get_contributor_by_name(repository, person).available_on = curr_day + \
                                                               find_project_in_repo(repository, j[0]).num_of_days
            remove_project_from_repository(repository, j[0])
        full_answer += result
        curr_day += 1
    create_output(full_answer)


if __name__ == '__main__':
    main("./examples/a_an_example.in.txt")
