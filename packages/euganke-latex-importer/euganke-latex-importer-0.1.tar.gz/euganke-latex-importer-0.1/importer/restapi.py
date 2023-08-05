import fnmatch
import os
import json

from requests import Session


class RestApi(object):
    def __init__(
        self, url, userid, group=None, imagedir=None, type=None
    ):
        assert userid, "Userid must be set"

        self.url = url
        self.group = group
        self.imagedir = imagedir
        self.type = type
        self.s = Session()
        self.s.headers.update({
            "Authorization": userid
        })

        if self.group:
            r = self.get("/groups", params={
                "filter[where][name]": self.group
            })
            assert r, "Group %s does not exist" % self.group
            self.groupId = r[0]["id"]

    def get(self, url, params=None):
        return self.request("GET", url, params=params)

    def put(self, url, data=None, params=None, files=None):
        return self.request("PUT", url, data=data, params=params, files=files)

    def post(self, url, data=None, params=None, files=None):
        return self.request("POST", url, data=data, params=params, files=files)

    def delete(self, url):
        return self.request("DELETE", url)

    def request(self, type, url, data=None, params=None, files=None):
        # Requests encodes params wrong
        url = "%s%s" % (self.url, url)
        if params:
            url += "?" + "&".join(
                ["%s=%s" % (k, v) for k, v in params.iteritems()])

        if not files:
            headers = {"Content-Type": "application/json"}
        else:
            headers = None

        if data:
            data = json.dumps(data)

        r = self.s.request(type, url, data=data, files=files, headers=headers)
        if r.status_code != 200 and r.status_code != 204:
            print r.text
            return None

        try:
            return r.json()
        except:
            return r.text

    def update_exercise(self, exercise, replace=True, replace_img=False):
        """
        Update an exercise in the database. If there exist an exercise in the
        database with the same meta field "id" it is overwriten. Otherwise a
        new exercise is created
        """

        ex_data = {}

        # check if there is exercise with specific meta:id
        for k, v in exercise["meta"].iteritems():
            if k == "id":
                exid = v

        # Set sequential question ids
        for i, q in enumerate(exercise.get("questions", [])):
            q["id"] = i

        # Set group
        if self.group:
            ex_data["groupId"] = self.groupId

        # Set title
        ex_data["title"] = exercise["title"]

        # Make it public
        ex_data["public"] = True

        # Make it non visible
        ex_data["visible"] = False

        # Take exercise metadata
        ex_data["meta"] = exercise.pop("meta", {})

        # Take exercise tags
        ex_data["tags"] = exercise.pop("tags", [])
        ex_data["tags"] = [tag["value"] for tag in ex_data["tags"]]

        # Set exercise type
        ex_data["meta"]["type"] = self.type

        # The rest is exercise
        ex_data["data"] = exercise

        resources = exercise.pop("resources", None)

        filter = {
            "filter[where][and][0][meta.type]": self.type
        }
        if exid.isdigit():
            filter.update({"filter[where][and][1][meta.id][like]": "^%s$" % exid})
        else:
            filter.update({"filter[where][and][1][meta.id]": exid})
        if self.groupId.isdigit():
            filter.update({"filter[where][and][2][groupId][like]": "^%s$" % self.groupId})
        else:
            filter.update({"filter[where][and][2][groupId]": self.groupId})

        print "Checking for exixting exercise with id %s..." % exid
        r = self.get("/exercises", params=filter)
        if r is None:
            raise "Request error"

        if r:
            rexercise = r[0]
            print "found existing exercise"
        else:
            rexercise = None

        # if there is try to overwrite it with PUT
        if rexercise:
            if replace:
                print "Updating the exercise ...",

                rexercise = self.put(
                    "/exercises/%s" % rexercise['id'], data=ex_data
                )
            else:
                print "Not replacing!"
        # if there is no existing exercise, try to create one with POST
        else:
            print "POSTing new exercise ...",
            rexercise = self.post(
                "/exercises",
                data=ex_data
            )

        if rexercise is not None:
            print "OK"
        else:
            print "FAILED"
            return False

        # Save exercise id for image upload
        exid = rexercise["id"]

        if replace and "_resources" in rexercise:
            r = self.delete("/exercises/%s/resources" % exid)
            del rexercise["_resources"]

        # Upload IMAGES
        if resources and len(resources) > 0:
            resources = {r['resourceid']: r for r in resources}.values()
            for img in resources:
                rid = img["resourceid"]
                for file in os.listdir(self.imagedir):
                    if fnmatch.fnmatch(file, rid + '.*'):
                        image = file
                        break
                try:
                    files = {
                        'file': open(os.path.join(self.imagedir, image), 'rb')
                    }
                except:
                    print "Couldn't find image file for %s" % rid
                    return False

                rresources = [e["id"] for e in rexercise["_resources"]] \
                    if "_resources" in rexercise else []
                if img["resourceid"] not in rresources:
                    print "Uploading resource %s" % img["resourceid"]
                    r = self.post(
                        "/exercises/%s/resources/upload" % exid,
                        files=files
                    )
                    if not r:
                        print "Could not upload resource with id %s" % img["resourceid"]
                        return False

                    rid = r["id"]
                    r.update({"id": img["resourceid"]})
                    r = self.put(
                        "/exercises/%s/resources/%s" % (exid, rid),
                        data=r
                    )
                    if not r:
                        print "Could not update id of resource with id %s" % img["resourceid"]
                        return False
                elif img["resourceid"] in rresources and replace:
                    print "Replacing resource %s" % img["resourceid"]
                    r = self.post(
                        "/exercises/%s/resources/%s/upload" % (exid, img["resourceid"]),
                        files=files
                    )
                    if not r:
                        print "Could not upload resource with id %s" % img["resourceid"]
                        return False

        return True
