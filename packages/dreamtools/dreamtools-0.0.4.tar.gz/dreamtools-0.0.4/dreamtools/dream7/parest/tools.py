"""tools module provides basic tools to help in data mining of 


author: Thomas Cokelaer, cokelaer@ebi.ac.uk
"""
import os
import tempfile
import tarfile

# true for all challenges
valid_extensions = ['doc', 'docx', 'txt', 'rtf']



def cleanup_tar_ball(tarball=None, files_per_team=2, team_to_remove=[], verbose=True):
    """Extract all latest submissions from a tar ball and creates an expurged one 

    :Description:

    During Dream submission, a team may resubmit files several times. 
    the first submission has a generic name as follows::
    
        dream6_challenge_team.txt

    If resubmission is made, a new file is created. The filename is changed 
    with a number appended at the end (starting with zero)::

        dream6_challenge_team_0.txt

    .. note:: The final number is incremented each time a new submission is made. Since the first 
        submission has no number, the second submission is tagged with the number 0.

    Since the latest submitted file is the one that matters, we want to remove the 
    other one in the expurged tar ball.

    So, this function keeps only the latest version of each generic file found in the original tar ball.

    :param tarball: a valid tar ball (zipped or not)
    :param files_per_team: the expected files per team in the tar ball. Not very important. 
        It is used to print information on the stdout.
    :param team_to_remove: sometimes, test were performed. We do not want some teams to be kept.
    :param verbose: verbose True by default.

    :Example:

        >>> import dreamtools
        >>> from dreamtools import tools
        >>> from tools import cleanup_tar_ball
        >>> cleanup_tar_ball('data.tar.gz')

    It will read the tar ball, select only a subset of files and save them in a new tar ball. 
    The original one is therefore untouched. The new one is saved in a temporary directory  
    /tmp under Linux. A print statement should tell you where the file is saved.

    .. warning:: the tar ball has to be a flat structure. This script is not currently dealing with tree
        directories within the tar ball.
    """
    # check that the file exists.
    if os.path.exists(tarball):
        pass
    else:
        raise IOError('invalid tarball name provided')

    # reading the tar ball file and extract all filenames
    tar = tarfile.open(tarball)
    print 'The tar ball contains %s entries. Scanning the filenames:' % len(tar.getnames()) 

    # we do not want all the directories.
    all_filenames = []
    for tarinfo in tar:
        if tarinfo.isreg():
            # Possibly, we remove some files in their team name match those to be removed
            if any([name in tarinfo.name for name in team_to_remove]) is False:
                all_filenames.append(tarinfo.name)
                if verbose == True:
                    print "----- Found a regular file called", tarinfo.name
            else:
                if verbose == True:
                    print '***** %s is removed as requested' % (tarinfo.name)
        elif tarinfo.isdir():
            if verbose == True:
                print ">>>>> Found a directory %s. Skip it." % tarinfo.name
        else:
            raise ValueError("not a file, not adirectory !!")

    print("------------------------------------------")
    if len(all_filenames) == 0:
        raise ValueError('tar ball seems empty')
    else:
        print 'The tar ball contains ' , len(all_filenames), 'files'

    # scan the list to get all filenames uploaded without the extension and 
    # first ignored all those that ends with a numeric

    # keep only the name without extension, get last value and check if it is a digit.
    files_to_keep = {}
    files_first_uploaded = []
    files_remaining = []
    
    # by default the first uploaded files does not end with underscore followed by a digit, 
    # so we rename it by appending a negative one (-1)
    # after this loop we must have found all the unique files
    for filename in all_filenames:
        name, ext = os.path.splitext(filename) 
        # split the name with underscore.
        # select the last word
        # check if it is numeric
        if name.split('_')[-1].isdigit() is False:
            files_first_uploaded.append(filename)
            files_to_keep[filename] = -1
        else:
            files_remaining.append(filename)

    if verbose == True:
        print 'Generic filenames to be kept are:'
        files2keep = files_to_keep.keys()
        files2keep.sort() 
        for f in files2keep:
            print '-----' , f
        print '------------------------------------------'
    print "Found %s teams (preliminary results)" % (len(files_to_keep) / files_per_team)

    # - all files in files_remaining must contain a number at the end
    # - only the file containing the maximum number is kept.

    for filename in files_remaining:
        name, ext = os.path.splitext(filename)  #split the filename extension
        name_without_digit = name.rpartition('_')[0]  # and digit
        key = name_without_digit +   ext              # build up the expected final file name used as keys in the dict
        number = int(name.rpartition('_')[-1])        # get the final number in the filename
        if key  not in files_to_keep.keys():
            print 'WARNING: found a new team... check it ', key
            files_to_keep[key] = number 
        elif number > files_to_keep[key]:                 # if greater than current maximum, update the dict
            files_to_keep[key] = number

    print "Found %s teams " % (len(files_to_keep) / files_per_team)
        
    files = {} #final filenames with key as the targeted filename and value as the input filename
    for key, value in files_to_keep.iteritems(): 
        name, ext = os.path.splitext(key)
        if value == -1:
            files[key] = name +  ext
        else:
            files[key] = name + '_%s' % value + ext

    # So, now we have a dictionary with keys as targete filenames and values 
    # as the filenames to copy (latest uploaded version)

    # create a temporary directory 
    d = tempfile.mkdtemp()
    
    # open a tar file (compressed)
    tar2 = tarfile.open(os.path.join(d, "sample.tar.gz"), mode='w:gz')

    # save all relevant files in it
    for target_name, original_name in files.iteritems():
        # First, extract some information
        print 'Saving ' , original_name
        info = tar.getmember(original_name)
        # and the relevant data to be saved
        data = tar.extractfile(original_name)
        # rename the info (should be done here not before reading the data) 
        info.name = target_name
        # save the file
        tar2.addfile(info, data)

    # closing after all data are written
    tar2.close()
   
    print '----> A tar ball file has been saved in ' + d 
    return d, files_to_keep
