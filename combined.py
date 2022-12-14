import csv,os

def getFileMatrix(fileName):
    """
    INPUT
    fileName: name of csv file, should be in same directory as this file
    OUTPUT
    2d list of values read from csv file
    """
    with open(fileName,"r") as csvfile:
        csvreader = csv.reader(csvfile)

        matrix = []

        for row in csvreader:
            matrix.append(row)
        
        return matrix

def getHeaderNameToColumnIndex(matrix):
    """
    INPUT:
    matrix: 2d list representing csv file
    OUTPUT:
    returns dict mapping headerNames to their columnIndex in the matrix
    """
    dict = {}
    for index,column in enumerate(matrix[0]):
        dict[column] = index
    return dict

def separateBySemicolons(info):
    """
    INPUT:
    info: string of values separated by semicolons or commas

    OUTPUT:
    convertedInfo: same string of values by separated by semicolons ONLY
    """
    data = []

    commaSeparatedInterestInfo = info.split(",")

    for value in commaSeparatedInterestInfo:
        data.append(value.strip())

    convertedInfo = ";".join(data)
    return convertedInfo

def convertToProperCSV(inputMatrixMinusHeaders,headerNameToColumnIndex,interestColumnName,leaderColumnName):
    """
    Takes in inputMatrixMinusHeaders and changes the delimeter of the values under interest/leader columns
    to semicolons if it's not already in that form
    """
    interestColumnIndex = headerNameToColumnIndex[interestColumnName]
    leaderColumnIndex = headerNameToColumnIndex[leaderColumnName]

    for rowIndex,row in enumerate(inputMatrixMinusHeaders):
        interestInfo = row[interestColumnIndex]
        leaderInfo = row[leaderColumnIndex]

        if len(interestInfo.split(";")) == 1 or len(leaderInfo.split(";")) == 1:
            inputMatrixMinusHeaders[rowIndex][interestColumnIndex] = separateBySemicolons(interestInfo)
            inputMatrixMinusHeaders[rowIndex][leaderColumnIndex] = separateBySemicolons(leaderInfo)

def findAllProjects(inputMatrixMinusHeaders,headerNameToColumnIndex,interestColumnName,leaderColumnName):
    """
    INPUT:
    inputMatrixMinusHeaders: matrix containing only student responses in each row
    headerNameToColumnIndex: dict mapping headerNames to corresponding columnIndex
    interestColumnName: name of column to look for project interest
    leaderColumnName: name of column to look for project leader interest

    OUTPUT:
    returns sorted list of all unique projects that have any interest from students and/or leaders
    """
    interestColumnIndex = headerNameToColumnIndex[interestColumnName]
    leaderColumnIndex = headerNameToColumnIndex[leaderColumnName]
    
    interestedProjectsSet = set()

    for row in inputMatrixMinusHeaders:
        interestProjects = row[interestColumnIndex]
        interestProjectsList = interestProjects.split(";")

        leaderProjects = row[leaderColumnIndex]
        leaderProjectsList = leaderProjects.split(";")

        if interestProjectsList[0] == '':
            interestProjectsList = []
        if leaderProjectsList[0] == '':
            leaderProjectsList = []
        
        for projectName in interestProjectsList + leaderProjectsList:
            interestedProjectsSet.add(projectName.strip())
    
    result = list(interestedProjectsSet)
    result.sort()
    return result

def makeProjectAssociations(projectNames):
    """
    INPUT
    projectNames: list of projectNames
    OUTPUT
    tuple of dicts: (projectNames to columnIndex, columnIndex to projectNames)
    Column Indices are generated here for use in creating a preference matrix
    """
    projectNameToIndex = {}
    indexToProjectName = {}
    index = 0

    for projectName in projectNames:
        projectNameToIndex[projectName] = index
        indexToProjectName[index] = projectName
        index += 1
    
    return (projectNameToIndex,indexToProjectName)

def getLeaderValue(inputMatrixMinusHeaders):
    """
    Finds leader value in order to differentiate between students and leaders. Leader
    value is guaranteed to be greater than the total number of students. Minimum value
    is 10.
    """
    totalStudents = len(inputMatrixMinusHeaders)
    leaderValue = 10

    while leaderValue < totalStudents:
        leaderValue *= 10
    
    return leaderValue

def addStudents(inputMatrixMinusHeaders,projectNamesToColumnIndex,headerNameToColumnIndex,
    leaderValue,interestColumnName,leaderColumnName,nameColumnName
):
    """
    INPUT
    leaderValue: value added to interested leaders for a certain project (to differentiate between normal students)
    OUTPUT
    preferences: 2d list where each student represents a student and each column represents a project.
    0 = no interest, 1 = interest, leaderValue + 1 = interested in leading project
    studentRowIndexToStudentName: Dict mapping student names to the corresponding row index in preferences matrix
    """
    studentRowIndexToStudentName = {}
    studentIndex = 0

    totalProjects = len(projectNamesToColumnIndex.keys())

    nameColumnIndex = headerNameToColumnIndex[nameColumnName]
    interestColumnIndex = headerNameToColumnIndex[interestColumnName]
    leaderColumnIndex = headerNameToColumnIndex[leaderColumnName]

    preferences = []

    for studentRow in inputMatrixMinusHeaders:
        personSummary = [0] * totalProjects

        studentRowIndexToStudentName[studentIndex] = studentRow[nameColumnIndex]
        studentIndex += 1

        interestProjects = studentRow[interestColumnIndex]
        leaderProjects = studentRow[leaderColumnIndex]

        interestProjectsList = interestProjects.split(";")
        leaderProjectsList = leaderProjects.split(";")

        if interestProjectsList[0] == '':
            interestProjectsList = []
        if leaderProjectsList[0] == '':
            leaderProjectsList = []

        for studentProject in interestProjectsList:
            personSummary[projectNamesToColumnIndex[studentProject]] = 1
        
        for leaderProject in leaderProjectsList:
            personSummary[projectNamesToColumnIndex[leaderProject]] = leaderValue + 1

        preferences.append(personSummary)
    
    return preferences, studentRowIndexToStudentName

def summarizePreferences(preferences):
    """
    OUTPUT
    summary: sorted list of tuples where each tuple contains projectNumber and the total interest in project.
    List is stored by total interest.
    """
    summary = []

    for projectNum in range(len(preferences[0])):
        projectSummary = [projectNum,0]
        for studentNum in range(len(preferences)):
            if preferences[studentNum][projectNum] > 0:
                projectSummary[1] += preferences[studentNum][projectNum]
        summary.append(projectSummary)
    
    summary.sort(key = lambda x: x[1])
    return summary

def findBestSplit(count,minSize,maxSize):
    """
    INPUT:
    count: number of students to split
    minSize: smallest team size considered to make equal teams
    maxSize: teams cannot surpass this size
    
    OUTPUT: (tuple)
    (bestSize, bestRemainder): size of each team, how many teams will have an extra member
    Goal is to minimize remainder, and maxamize team size
    """
    bestSize = None
    bestRemainder = None

    if count % maxSize == 0:
        return (maxSize,0)

    for size in range(minSize,maxSize)[::-1]:
        remainder = count % size
        if remainder == 0:
            return (size,0)
        elif not bestRemainder or remainder < bestRemainder:
            bestSize = size
            bestRemainder = remainder 
    
    if not bestSize:
        bestSize = maxSize
        bestRemainder = 0

    return (bestSize,bestRemainder)

def assignPlayersToProjects(summary,preferences,studentCount,minTeamSize,maxTeamSize,maxTeamsPerProject,leaderValue,leadersPerTeam=1):
    """
    OUTPUT (tuple)
    unluckyProjects: list of projects that do not have any teams working on them
    teamsAssigned: dict that contains all projects, and the teams that will be working on them
    sadPlayerCount: number of people that have not been assigned to a team
    """

    # each index in peopleTaken represents person, 1 => person has project
    peopleTaken = [0] * studentCount
    unluckyProjects = []
    teamsAssigned = {}

    minTeamSizeValue = leadersPerTeam * leaderValue + minTeamSize
    
    for currentSummaryI in range(len(summary)):
        projectSummary = summary[currentSummaryI]

        # no way team can be made if not enough interest (in general)
        if projectSummary[1] < minTeamSizeValue:
            unluckyProjects.append(projectSummary[0])
        else:
            studentsReady = []
            leadersReady = []

            # find all students and leaders interested in project (and are available)
            for studentIndex in range(len(preferences)):
                if peopleTaken[studentIndex] == 0:
                    if preferences[studentIndex][projectSummary[0]] == 1: 
                        studentsReady.append(studentIndex)
                    elif preferences[studentIndex][projectSummary[0]] == leaderValue + 1:
                        leadersReady.append(studentIndex)

            # check if there is enough available people to make a team, otherwise project is not happening
            if len(studentsReady) + len(leadersReady) < minTeamSize:
                unluckyProjects.append(projectSummary[0])
                continue

            # find best combo
            groupMin, remainder = findBestSplit(
                len(studentsReady)+len(leadersReady),
                minTeamSize,
                maxTeamSize
            )
            
            teamsCreated = []
            currentStudent = 0
            currentLeader = 0
            
            while currentLeader < len(leadersReady) and len(leadersReady) - currentLeader >= leadersPerTeam:
                newTeam = []
                # add specified number of leaders to team
                for _ in range(leadersPerTeam):
                    newTeam.append(leadersReady[currentLeader])
                    currentLeader += 1
                
                # fill in the rest of the spots with students
                lastPlayer = currentStudent + groupMin - leadersPerTeam
                if remainder > 0:
                    lastPlayer += 1
                    remainder -= 1
                newTeam += studentsReady[currentStudent:lastPlayer]
                currentStudent = lastPlayer

                # if no students left, but there are more leaders left, convert them to students
                if len(newTeam) < groupMin:
                    lastLeader = currentLeader + groupMin - len(newTeam) - 1
                    newTeam += leadersReady[currentLeader:lastLeader + 1]
                    currentLeader = lastLeader + 1

                teamsCreated.append(newTeam)
            
            # delete teams if too many
            teamsCreated = teamsCreated[:maxTeamsPerProject]

            # release last team if not enough members
            if teamsCreated and len(teamsCreated[-1]) < minTeamSize:
                for studentIndex in teamsCreated[-1]:
                    peopleTaken[studentIndex] = 0
                teamsCreated.pop()

            # change status of students in project to taken
            for team in teamsCreated:
                for person in team:
                    peopleTaken[person] = 1
            
            teamsAssigned[projectSummary[0]] = teamsCreated

    sadPlayerCount = len(peopleTaken) - sum(peopleTaken)
    unluckyProjects.sort()
    
    return unluckyProjects,teamsAssigned,sadPlayerCount

def getStudentInfo(fileMatrixWithoutHeaders,studentIndex,headerAssociations,columnsToInclude):
    """
    INPUT
    fileMatrixWithoutHeaders: matrix containing initial responses without the header row
    studentIndex: index of row corresponding to student
    headerAssociations: dict mapping columnNames to the columnIndex in the fileMatrix
    columnsToInclude: student responses these columns will be included
    
    OUTPUT (string)
    row: student responses to columns indicated from input file and formats them in CSV format
    """
    studentDetails = []

    for columnName in columnsToInclude:
        columnIndex = headerAssociations.get(columnName)
        info = fileMatrixWithoutHeaders[studentIndex][columnIndex]

        studentDetails.append(info)

    separator = '","'
    result = '"' + separator.join(studentDetails) + '"'
    return result

def createCSVfile(
    fileName,teamsAssigned,matrixMinusHeader,projectIndexToProjectName,
    headerNameToColumnIndex,columnsToInclude
):
    """
    INPUT:
    fileName: name of file to create with output
    teamsAssigned: dict of all projects and the teams working on each
    columnsToInclude: student responses to theses questions will be included in output

    OUTPUT: 
    None: CSV file is created with students listed under their assigned project
    """
    with open(fileName,"w") as file:
        for projectIndex in teamsAssigned.keys():
            
            file.write(f"{projectIndexToProjectName.get(projectIndex)}\n")
            
            teams = teamsAssigned.get(projectIndex)

            for team in teams:
                for studentIndex in team:
                    studentInfo = getStudentInfo(matrixMinusHeader,studentIndex,
                        headerNameToColumnIndex,columnsToInclude
                    )
                    file.write(f"{studentInfo}\n")

                file.write("\n")

# USER INPUT

INPUT_CSV_FILENAME = "openProj.csv"
INTEREST_COLUMN_NAME = "Interested?"
LEADER_COLUMN_NAME = "Interested in leading?"
NAME_COLUMN_NAME = "Name"

MIN_TEAM_SIZE = 2
MAX_TEAM_SIZE = 3
MAX_TEAMS_PER_PROJECT = 1
LEADERS_PER_TEAM = 2

OUTPUT_COLUMNS = ["Name","Email"]
OUTPUT_FILENAME = "CSVresult.csv"

# RUN USER CODE

RUN_USER_CODE = True
PRINT_RESULTS = True

if RUN_USER_CODE:
    inputMatrix = getFileMatrix(INPUT_CSV_FILENAME)
    inputMatrixMinusHeaders = inputMatrix[1:]
    LEADER_VALUE = getLeaderValue(inputMatrixMinusHeaders)

    headerNameToColumnIndex = getHeaderNameToColumnIndex(inputMatrix)
    convertToProperCSV(inputMatrixMinusHeaders,headerNameToColumnIndex,INTEREST_COLUMN_NAME,LEADER_COLUMN_NAME)

    allProjectList = findAllProjects(
        inputMatrixMinusHeaders, headerNameToColumnIndex,INTEREST_COLUMN_NAME,
        LEADER_COLUMN_NAME
    )

    projectAssociations = makeProjectAssociations(allProjectList)
    projectNamesToProjectIndex = projectAssociations[0]
    projectIndexToProjectNames = projectAssociations[1]

    preferences, studentNamesToRowIndex = addStudents(
        inputMatrixMinusHeaders, projectNamesToProjectIndex, headerNameToColumnIndex,
        LEADER_VALUE,INTEREST_COLUMN_NAME, LEADER_COLUMN_NAME, NAME_COLUMN_NAME
    )

    summary = summarizePreferences(preferences)

    unpopular, projectTeams, sadPeople = assignPlayersToProjects(
        summary, preferences, len(studentNamesToRowIndex.keys()), MIN_TEAM_SIZE,
        MAX_TEAM_SIZE, MAX_TEAMS_PER_PROJECT, LEADER_VALUE, LEADERS_PER_TEAM
    )

    if PRINT_RESULTS:
        print(f"\nsummary \n {summary}")
        print(f"\nunpopularProjects: {unpopular}")
        print(f"results: {projectTeams}")
        print(f"sadPeople: {sadPeople}")
    
    createCSVfile(
        OUTPUT_FILENAME,projectTeams,inputMatrixMinusHeaders,
        projectIndexToProjectNames,headerNameToColumnIndex,OUTPUT_COLUMNS
    )

# TESTS

RUN_TESTS = False

if RUN_TESTS:
    testCsvFileName = "testCSVprocess.csv"
    testNameColumnName = "Name"
    testInterestColumnName = "Interested?"
    testLeaderColumnName = "Leader?"

    testMinTeamSize = 2
    testMaxTeamSize = 3
    testMaxTeamsPerProject = 1

    testOutputColumns = ["Name","Timestamp"]
    testOutputFilename = "testCSVResult.csv"

    try:
        os.remove(testOutputFilename)
        print("deleted existing output file")
    except:
        print("no output file exists before execution")

    testInputMatrix = getFileMatrix(testCsvFileName)
    testInputMatrixMinusHeaders = testInputMatrix[1:]

    testLeaderValue = getLeaderValue(testInputMatrixMinusHeaders)

    testHeaderNameToColumnIndex = getHeaderNameToColumnIndex(testInputMatrix)
    assert(len(testHeaderNameToColumnIndex) == 5)
    assert(testHeaderNameToColumnIndex[testNameColumnName] == 1)
    assert(testHeaderNameToColumnIndex[testInterestColumnName] == 3)
    assert(testHeaderNameToColumnIndex[testLeaderColumnName] == 4)

    testAllProjectList = findAllProjects(
        testInputMatrixMinusHeaders,testHeaderNameToColumnIndex,testInterestColumnName,testLeaderColumnName
    )
    assert(testAllProjectList == ["Blu","Gre","Red","Yel"])

    testProjectAssociations = makeProjectAssociations(testAllProjectList)
    testProjectNamesToProjectIndex = testProjectAssociations[0]
    testProjectIndexToProjectNames = testProjectAssociations[1]

    assert(len(testProjectNamesToProjectIndex.keys()) == 4)
    assert(testProjectNamesToProjectIndex["Blu"] == 0)
    assert(testProjectNamesToProjectIndex["Gre"] == 1)
    assert(testProjectNamesToProjectIndex["Red"] == 2)
    assert(testProjectNamesToProjectIndex["Yel"] == 3)

    assert(len(testProjectIndexToProjectNames.keys()) == 4)
    assert(testProjectIndexToProjectNames.get(0) == "Blu")
    assert(testProjectIndexToProjectNames.get(1) == "Gre")
    assert(testProjectIndexToProjectNames.get(2) == "Red")
    assert(testProjectIndexToProjectNames.get(3) == "Yel")

    testPreferences, testStudentNamesToRowIndex = addStudents(
        testInputMatrixMinusHeaders,testProjectNamesToProjectIndex,testHeaderNameToColumnIndex,testLeaderValue,
        testInterestColumnName,testLeaderColumnName,testNameColumnName
    )

    assert(testPreferences == [
        [1,                 0,                  testLeaderValue+1,  0           ],
        [testLeaderValue+1, testLeaderValue+1,  0,                  0           ],
        [testLeaderValue+1, 1,                  testLeaderValue+1,  testLeaderValue+1]
    ])

    assert(len(testStudentNamesToRowIndex.keys()) == 3)
    assert(testStudentNamesToRowIndex.get(0) == "Breach")
    assert(testStudentNamesToRowIndex.get(1) == "Cypher")
    assert(testStudentNamesToRowIndex.get(2) == "Raze")

    testSummary = summarizePreferences(testPreferences)
    assert(testSummary == [
        [3,testLeaderValue + 1],
        [1,testLeaderValue + 1 + 1],
        [2,2*(testLeaderValue + 1)],
        [0,2*(testLeaderValue + 1) + 1]
    ])

    testUnpopular, testProjectTeams, testSadPeople = assignPlayersToProjects(
        testSummary, testPreferences, len(testStudentNamesToRowIndex.keys()), testMinTeamSize, 
        testMaxTeamSize, testMaxTeamsPerProject, testLeaderValue
    )

    assert(testUnpopular == [0,2,3])
    assert(len(testProjectTeams.keys()) == 1)

    testOnlyTeam = testProjectTeams[1][0]
    testOnlyTeam.sort()

    assert(testOnlyTeam == [1,2])
    assert(testSadPeople == 1)

    testResult = getStudentInfo(
        testInputMatrixMinusHeaders,0,
        testHeaderNameToColumnIndex,testOutputColumns
    )
    assert(testResult == '"Breach","2022/11/10 5:45:46 PM PST"')

    createCSVfile(
        testOutputFilename,testProjectTeams,testInputMatrixMinusHeaders,
        testProjectIndexToProjectNames,testHeaderNameToColumnIndex,testOutputColumns
    )

    testResult = getFileMatrix(testOutputFilename)
    assert(testResult[0] == ["Gre"])
    assert(testResult[1] == ["Cypher","2022/11/10 5:45:49 PM PST"])
    assert(testResult[2] == ["Raze","2022/11/10 5:45:52 PM PST"])

    # testing csv conversion to matrix

    testInputMatrixMinusHeaders = [
        ["",""],
        ["red",""],
        ["","blu"],
        ["red, blu",""],
        ["","red, blu"],
        ["red, blu", "red,blu"],
        ["red;blu", "red;blu"]
    ]
    testInterestColumnName = "interest"
    testLeaderColumnName = "leader"
    testHeaderNameToColumnIndex = {testInterestColumnName:0,testLeaderColumnName:1}

    convertToProperCSV(testInputMatrixMinusHeaders,testHeaderNameToColumnIndex,testInterestColumnName,testLeaderColumnName)

    assert (testInputMatrixMinusHeaders == [
        ["",""],
        ["red",""],
        ["","blu"],
        ["red;blu",""],
        ["","red;blu"],
        ["red;blu", "red;blu"],
        ["red;blu", "red;blu"]
    ])

    # testing best splits

    assert(findBestSplit(21,5,7) == (7,0))
    assert(findBestSplit(16,5,7) == (5,1))
    assert(findBestSplit(10,5,8) == (5,0))
    assert(findBestSplit(3,3,4) == (3,0))

    # testing team assignment

    testPreferences = [
        [10001, 0,      0],
        [1,     0,      0],
        [0,     0,  10001],
        [10001, 0,      0],
        [0,     0,      1],
        [0,     10001,  0],
        [0,     10001,  0],
        [0,     0,  10001],
        [1,     0,      1],
        [0,     10001,  1]
    ]

    testSummary = summarizePreferences(testPreferences)
    assert(testSummary == [[0,20004],[2,20005],[1,30003]])

    testNumberOfLeaders = 2
    testUnluckyProjects, testTeamsAssigned, testSadCount = assignPlayersToProjects(
        testSummary,testPreferences,len(testPreferences),3,4,1,10000,testNumberOfLeaders
    )

    for projectNumber, teams in testTeamsAssigned.items():
        for team in teams:
            for i in range(testNumberOfLeaders):
                assert(testPreferences[team[i]][projectNumber] > 1)

    testNumberOfLeaders = 3
    testUnluckyProjects, testTeamsAssigned, testSadCount = assignPlayersToProjects(
        testSummary,testPreferences,len(testPreferences),3,4,1,10000,testNumberOfLeaders
    )

    for projectNumber, teams in testTeamsAssigned.items():
        for team in teams:
            for i in range(testNumberOfLeaders):
                assert(testPreferences[team[i]][projectNumber] > 1)

    # testing team assignment bug

    testPreferences = [
        [10001, 0],
        [1,     0],
        [10001, 0],
        [10001, 0]
    ]

    testSummary = summarizePreferences(testPreferences)
    assert(testSummary == [[1,0],[0,30004]])

    testNumberOfLeaders = 2
    testUnluckyProjects, testTeamsAssigned, testSadCount = assignPlayersToProjects(
        testSummary,testPreferences,len(testPreferences),3,3,1,10000,testNumberOfLeaders
    )

    for projectNumber, teams in testTeamsAssigned.items():
        for team in teams:
            for i in range(testNumberOfLeaders):
                assert(testPreferences[team[i]][projectNumber] > 1)

    # testing leaderValue generation

    testInputMatrixMinusHeaders = []

    for _ in range(259):
        testInputMatrixMinusHeaders.append([])
    
    testLeaderValue = getLeaderValue(testInputMatrixMinusHeaders)
    assert(testLeaderValue == 1000)

    print("tests passed")