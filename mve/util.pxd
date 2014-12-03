cdef extern from 'util/ref_ptr.h' namespace 'util' nogil:
    cdef cppclass RefPtr[T]:
        RefPtr() except +
        RefPtr(T*) except +
        RefPtr(RefPtr&) except +
        void reset()
        int use_count()
        T* get()
        void swap(RefPtr&)
        T& operator*()
        #T* operator->()
        #RefPtr& operator=(RefPtr&)
        #RefPtr& operator=(T*)
        bint operator==(T*)
        bint operator==(RefPtr&)
        bint operator!=(T*)
        bint operator!=(RefPtr&)


