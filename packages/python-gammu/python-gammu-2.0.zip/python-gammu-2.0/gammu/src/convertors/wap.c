/*
 * python-gammu - Phone communication libary
 * Copyright © 2003 - 2010 Michal Čihař
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the Free
 * Software Foundation; either version 2 of the License.
 *
 * This program is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
 * more details.
 *
 * You should have received a copy of the GNU General Public License along with
 * this program; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 *
 * vim: expandtab sw=4 ts=4 sts=4:
 */

/* MMS and WAP related conversions */
#include "convertors.h"

char *MMSClassToString(GSM_MMS_Class c)
{
	char *s = NULL;

	switch (c) {
		case GSM_MMS_Personal:
			s = strdup("Personal");
			break;
		case GSM_MMS_Advertisement:
			s = strdup("Advertisement");
			break;
		case GSM_MMS_Info:
			s = strdup("Info");
			break;
		case GSM_MMS_Auto:
			s = strdup("Auto");
			break;
		case GSM_MMS_None:
		case GSM_MMS_INVALID:
			s = strdup("");
			break;
	}

	if (s == NULL) {
		PyErr_Format(PyExc_ValueError,
			     "Bad value for MMS Class from Gammu: '%d'", c);
		return NULL;
	}

	return s;
}

GSM_MMS_Class MMSClassFromString(const char *s)
{
	if (strcmp("Personal", s) == 0)
		return GSM_MMS_Personal;
	else if (strcmp("Advertisement", s) == 0)
		return GSM_MMS_Advertisement;
	else if (strcmp("Info", s) == 0)
		return GSM_MMS_Info;
	else if (strcmp("Auto", s) == 0)
		return GSM_MMS_Auto;
	else if (strcmp("", s) == 0)
		return GSM_MMS_None;
	PyErr_Format(PyExc_MemoryError, "Bad value for MMS Class Type '%s'", s);
	return GSM_MMS_INVALID;
}

PyObject *MMSIndicatorToPython(GSM_MMSIndicator * mms)
{
	char *class;
	PyObject *ret;

	class = MMSClassToString(mms->Class);
	if (class == NULL) {
		return NULL;
	}
	ret = Py_BuildValue("{s:s,s:s,s:s,s:i,s:s}",
			     "Address", mms->Address,
			     "Title", mms->Title,
			     "Sender", mms->Sender,
			     "MessageSize", (int)mms->MessageSize,
			     "Class", class);
	free(class);
	return ret;
}

int MMSIndicatorFromPython(PyObject * dict, GSM_MMSIndicator * mms)
{
	char *s;

	if (!PyDict_Check(dict)) {
		PyErr_Format(PyExc_ValueError,
			     "MMSIndicator is not a dictionary");
		return 0;
	}

	memset(mms, 0, sizeof(GSM_MMSIndicator));

	s = GetCharFromDict(dict, "Address");
	if (strlen(s) > 499) {
		PyErr_Format(PyExc_ValueError, "Address too long!");
		free(s);
		return 0;
	}
	strcpy(s, mms->Address);
	free(s);

	s = GetCharFromDict(dict, "Title");
	if (strlen(s) > 499) {
		free(s);
		PyErr_Format(PyExc_ValueError, "Title too long!");
		return 0;
	}
	strcpy(s, mms->Title);
	free(s);

	s = GetCharFromDict(dict, "Sender");
	if (strlen(s) > 499) {
		free(s);
		PyErr_Format(PyExc_ValueError, "Sender too long!");
		return 0;
	}
	strcpy(s, mms->Sender);
	free(s);

	mms->MessageSize = GetIntFromDict(dict, "MessageSender");
	if (mms->MessageSize == INT_INVALID) {
		mms->MessageSize = 0;
	}

	s = GetCharFromDict(dict, "Class");
	if (s != NULL) {
		mms->Class = MMSClassFromString(s);
		free(s);
		if (mms->Class == GSM_MMS_INVALID) {
			return 0;
		}
	}

	return 1;
}

PyObject *WAPBookmarkToPython(GSM_WAPBookmark * wap)
{
	PyObject *ret;
	Py_UNICODE *title, *address;

	title = strGammuToPython(wap->Title);
	if (title == NULL)
		return NULL;

	address = strGammuToPython(wap->Address);
	if (address == NULL)
		return NULL;

	ret = Py_BuildValue("{s:s,s:s,s:i}",
			    "Address", address,
			    "Title", title, "Location", wap->Location);

	free(title);
	free(address);

	return ret;
}

int WAPBookmarkFromPython(PyObject * dict, GSM_WAPBookmark * wap)
{
	if (!PyDict_Check(dict)) {
		PyErr_Format(PyExc_ValueError,
			     "WAPBookmark is not a dictionary");
		return 0;
	}

	memset(wap, 0, sizeof(GSM_WAPBookmark));

	wap->Location = GetIntFromDict(dict, "Location");
	if (wap->Location == INT_INVALID)
		return 0;

	if (!CopyStringFromDict(dict, "Address", 255, wap->Address))
		return 0;

	if (!CopyStringFromDict(dict, "Title", 50, wap->Title))
		return 0;

	return 1;
}

/*
 * vim: noexpandtab sw=8 ts=8 sts=8:
 */
