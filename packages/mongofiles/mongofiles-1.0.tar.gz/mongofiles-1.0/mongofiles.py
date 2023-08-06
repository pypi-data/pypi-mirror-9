#!/usr/bin/env python
"""
mongofiles for Humans

Official [mongofiles][mongofiles] --db and --collection arguments don't work as expected,
so I re-written mongofiles in Python for humans.

See also
 - http://dirolf.com/2010/03/29/new-gridfs-implementation-for-pymongo.html

[mongofiles]: https://github.com/mongodb/mongo-tools/tree/master/mongofiles
"""
import mimetypes
import os
import tempfile
import bson
import gridfs
import pymongo
import argparse


def get_gfs_and_col(args):
    root_collection = args.collection
    conn = pymongo.MongoClient(host=args.host, port=args.port)
    db = conn[args.db]

    gfs = gridfs.GridFS(database=db, collection=root_collection)

    collection = root_collection + '.files'
    col = db[collection]

    return gfs, col


def gridfs_list(args):
    gfs, collection = get_gfs_and_col(args)

    for doc in collection.find():
        filename = doc.get('filename')
        if filename:
            print "%s\t%s\t%d" % (doc['_id'], filename, doc['length'])


def gridfs_search(args):
    assert args.filename

    gfs, collection = get_gfs_and_col(args)

    for doc in collection.find():
        filename = doc.get('filename')
        if filename and filename.find(args.filename) != -1:
            print "%s\t%s\t%d" % (doc['_id'], filename, doc['length'])
            break


def gridfs_put(args):
    assert args.filepath

    filepath = os.path.realpath(args.filepath)

    gfs, collection = get_gfs_and_col(args)

    if args.local:
        filename = args.local
    else:
        # filename = filepath
        filename = os.path.basename(filepath)

    if args.type:
        content_type = args.type
    else:
        content_type = None

    if args.replace:
        for gout in gfs.find(dict(filename=filename)):
            gfs.delete(file_id=gout._id)
            print 'removed file', gout._file

    with open(filepath, 'rb') as f:
        _id = gfs.put(data=f, filename=filename, content_type=content_type)
        gout = gfs.get(file_id=_id)
        print 'added file:', gout._file


def gridfs_get(args):
    BUFF_SIZE = 8192
    assert args.filename or args.doc_id

    gfs, collection = get_gfs_and_col(args)

    def save_gout(gout):
        if gout.filename:
            fn, ext = os.path.splitext(os.path.basename(gout.filename))
        else:
            fn = args.doc_id

        ct = gout.content_type or 'application/octet-stream'
        ext = mimetypes.guess_extension(ct)

        folder_temp = tempfile.mkdtemp()
        save_to = os.path.join(folder_temp, fn + ext)

        with open(save_to, 'w') as f:
            while True:
                buf = gout.read(BUFF_SIZE)
                if not buf:
                    break
                f.write(buf)
            print 'done write to:', save_to

    if args.filename:
        for gout in gfs.find({'filename': args.filename}):
            save_gout(gout)

    elif args.doc_id:
        gout = gfs.get(file_id=bson.ObjectId(args.doc_id))
        save_gout(gout)


def gridfs_delete(args):
    assert args.filename or args.doc_id

    assert args.filename or args.doc_id

    gfs, collection = get_gfs_and_col(args)

    if args.filename:
        if args.filename != '*':
            gfs.delete({'filename': args.filename})
        else:
            for doc in collection.find():
                gfs.delete(file_id=doc['_id'])

            root_collection_name = collection.name[:collection.name.find('.')]
            col_name = root_collection_name + '.chunks'
            collection.database[col_name].remove()

    elif args.doc_id:
        gfs.delete(file_id=bson.ObjectId(args.doc_id))

    print 'done!'

def main(args):
    handle_map = {
        'list': gridfs_list,
        'search': gridfs_search,
        'put': gridfs_put,
        'get': gridfs_get,
        'delete': gridfs_delete,
    }

    print 'connected to: %s:%d' % (args.host, args.port)

    for key in handle_map.keys():
        if getattr(args, key):
            func = handle_map[key]
            func(args)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False)

    group_action = parser.add_mutually_exclusive_group()

    group_action.add_argument('--list', action="store_true")
    group_action.add_argument('--search', action="store_true")
    group_action.add_argument('--put', action="store_true")
    group_action.add_argument('--get', action="store_true")
    group_action.add_argument('--delete', action="store_true")

    parser.add_argument('-h', '--host', default='127.0.0.1', help='mongo host to connect to ( <set name>/s1,s2 for sets)')
    parser.add_argument('-p', '--port', default=27017, type=int, help='server port. Can also use --host hostname:port')
    parser.add_argument('-d', '--db', default='test', help='database to use')
    parser.add_argument('-c', '--collection', default='fs', help='collection to use (some commands)')
    parser.add_argument('-l', '--local', help="local filename for put|get (default is to use the same name as 'gridfs filename')")
    parser.add_argument('-t', '--type', help='MIME type for put (default is to omit)')
    parser.add_argument('-r', '--replace', action="store_true", help='Remove other files with same name after PUT')

    group_primary_key = parser.add_mutually_exclusive_group()
    group_primary_key.add_argument('--filename', help='gridfs <root_collection>.files filename')
    group_primary_key.add_argument('--doc_id', help='gridfs <root_collection>.files _id')

    group_primary_key.add_argument('--filepath', help='filepath to put')

    parser.add_argument('--help', action="help", help='produce help message')

    args = parser.parse_args()

    if args.list or args.search or args.put or args.get or args.delete:
        main(args)
    else:
        parser.print_help()
    exit(0)

