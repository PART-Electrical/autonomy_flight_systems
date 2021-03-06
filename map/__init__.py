import json
from mavsdk.mission import (MissionItem, MissionPlan)


class Map():
    """
    This class contains the methods and data used for routing the aircraft

    Expected input: mission_data - path to the .json file containing the mission data
    """

    def __init__(self, mission_data):
        file = json.load(open(mission_data, 'rb'))
        # This will contain a LocationGlobalRelative object for the current destination
        self.currentDest = None
        waypoints = []
        boundarypoints = []
        searchGridPoints = []

        # Looping through the waypoint dicts to load GPS cords
        for waypoint in file["waypoints"]:
            waypoints += [[waypoint["latitude"],
                           waypoint["longitude"], waypoint["altitude"]]]

        # Looping through the flyzone boundary dicts to load proper GPS cords
        for boundarypoint in file["flyZones"][0]["boundaryPoints"]:
            boundarypoints += [[boundarypoint["latitude"],
                                boundarypoint["longitude"]]]

        # Looping through the search grid dict to load GPS coords
        for searchpoint in file["searchGridPoints"]:
            searchGridPoints += [[searchpoint["latitude"],
                                  searchpoint["longitude"]]]

        # Contains flight data in a dict with easy access coords
        self.data = {"waypoints": waypoints,
                     "boundary": boundarypoints, "searchGrid": searchGridPoints}

    def generateWaypoint(self, plane, coordinate):
        """
        This will take in GPS coordinates and feed it to the drone.

        Expected input: plane (connection.py Object) - object containing the Dronekit vehicle. Used to feed the destination to the drone
            coordinate (tuple) - a tuple containing the desired ending GPS coordinates [latitude, longitude, altitude]

        Expected output: Returns a waypoint that can be fed to dronekit (sets the current destination to the provided coordinate)
        """
        self.currentDest = MissionItem(coordinate[0], coordinate[1], coordinate[2],
                                       10,
                                       True,
                                       float('nan'),
                                       float('nan'),
                                       MissionItem.CameraAction.NONE,
                                       float('nan'),
                                       float('nan'))
        return self.currentDest

    def breakWaypoints(self, waypointOne, waypointTwo, breakAmount=10):
        """
        This method will take in two waypoints and break it up into multiple waypoints along a line connecting the
        original two waypoints.

        Expected input: waypointOne (tuple) - a tuple containing the starting GPS coordinates [latitude, longitude, altitude]
            waypointTwo (tuple) - a tuple containing the desired ending GPS coordinates [latitude, longitude, altitude]
            breakAmount (int) - describes how many addional waypoints are wanted. By default, the function create ten extra points. 

        Expected output: returns a list containing all the new waypoints in order of occurance along the line between the two points
        """
        waypointList = []
        for stepNumber in range(1, breakAmount + 1):
            waypointList.append({"latitude": self.generateStep(stepNumber, waypointOne["latitude"], waypointTwo["latitude"], breakAmount),
                                 "longitude": self.generateStep(stepNumber, waypointOne["longitude"], waypointTwo["longitude"], breakAmount),
                                 "altitude": self.generateStep(stepNumber, waypointOne["altitude"], waypointTwo["latitude"], breakAmount)})

        return waypointList

    def generateStep(self, stepNumber, paramPointOne, paramPointTwo, breakAmount):
        return paramPointOne + round((stepNumber * (paramPointTwo - paramPointOne) / float(breakAmount)), 8)

    def changeRoute(self, route, targetWaypoint, newRoute):
        """
        This method will take in a list, targetWaypoint (coordiantes), and a new list. It will chop the original list at the specified
        waypoint and input the new list tuples after that point. It will finally return this newly created list.

        Expected input: route (list) - a list that needs to be changed containing tuples containing GPS coordinates [latitude, longitude, altitude]
            waypoint (tuple) - a tuple containing the desired chopping GPS coordinates [latitude, longitude, altitude]
            newRoute (list) - a new list that will replace tuples following chopPoint containing tuples containing GPS coordinates [latitude, longitude, altitude]

        Expected output: returns a list containing all the new waypoints in order of occurance along the line between the two points, or False if the target is not in the route.
        """
        if targetWaypoint in route:
            return (route[0:route.index(targetWaypoint)] + newRoute)
        else:
            return False


if __name__ == "__main__":
    route = Route("interop_example.json")
    print(route.data["boundary"])
    print(route.data["waypoints"])
    print(route.data["searchGrid"])
