// **********************************************************************
//
// Copyright (c) 2003-2014 ZeroC, Inc. All rights reserved.
//
// This copy of Ice is licensed to you under the terms described in the
// ICE_LICENSE file included in this distribution.
//
// **********************************************************************

#include <Ice/RequestHandlerFactory.h>
#include <Ice/CollocatedRequestHandler.h>
#include <Ice/ConnectRequestHandler.h>
#include <Ice/CollocatedRequestHandler.h>
#include <Ice/Reference.h>
#include <Ice/ObjectAdapterFactory.h>
#include <Ice/Instance.h>

using namespace std;
using namespace IceInternal;

RequestHandlerFactory::RequestHandlerFactory(const InstancePtr& instance) : _instance(instance)
{
}

RequestHandlerPtr 
IceInternal::RequestHandlerFactory::getRequestHandler(const ReferencePtr& ref, const Ice::ObjectPrx& proxy)
{
    if(ref->getCollocationOptimized())
    {
        Ice::ObjectAdapterPtr adapter = _instance->objectAdapterFactory()->findObjectAdapter(proxy);
        if(adapter)
        {
            return new CollocatedRequestHandler(ref, adapter);
        }
    }

    if(ref->getCacheConnection())
    {
        Lock sync(*this);
        
        map<ReferencePtr, RequestHandlerPtr>::iterator p = _handlers.find(ref);
        if(p != _handlers.end())
        {
            return p->second;
        }
        
        RequestHandlerPtr handler = new ConnectRequestHandler(ref, proxy);
        _handlers.insert(make_pair(ref, handler));
        return handler;
    }
    else
    {
        return new ConnectRequestHandler(ref, proxy);
    }
}

void 
IceInternal::RequestHandlerFactory::removeRequestHandler(const ReferencePtr& ref, const RequestHandlerPtr& handler)
{
    if(ref->getCacheConnection())
    {
        Lock sync(*this);
        map<ReferencePtr, RequestHandlerPtr>::iterator p = _handlers.find(ref);
        if(p != _handlers.end() && p->second.get() == handler.get())
        {
            _handlers.erase(p);
        }
    }
}

