#ifndef COLIBRIDATATYPES_H
#define COLIBRIDATATYPES_H

#include <string>
#include <iostream>
#include <ostream>
#include <istream>
#include <vector>
#include <set>
#include <algorithm>
#include "common.h"
#include "pattern.h"
#include "datatypes.h"
#include "classdecoder.h"


class IndexReference {
    /* Reference to a position in the corpus */
   public:
    uint32_t sentence;
    uint16_t token;
    IndexReference() { sentence=0; token = 0; } 
    IndexReference(uint32_t sentence, uint16_t token ) { this->sentence = sentence; this->token = token; }  
    IndexReference(std::istream * in) {
        in->read( (char*) &sentence, sizeof(uint32_t)); 
        in->read( (char*) &token, sizeof(uint16_t)); 
    }
    IndexReference(const IndexReference& other) { //copy constructor
        sentence = other.sentence;
        token = other.token;
    };     
    void write(std::ostream * out) const {
        out->write( (char*) &sentence, sizeof(uint32_t)); 
        out->write( (char*) &token, sizeof(uint16_t)); 
    }
    bool operator< (const IndexReference& other) const {
        if (sentence < other.sentence) {
            return true;
        } else if (sentence == other.sentence) {
            return (token < other.token);
        } else {
            return false;
        }
    }
    bool operator> (const IndexReference& other) const {
        return other < *this;
    }
    bool operator==(const IndexReference &other) const { return ( (sentence == other.sentence) && (token == other.token)); };
    bool operator!=(const IndexReference &other) const { return ( (sentence != other.sentence) || (token != other.token)); };
    IndexReference operator+(const int other) const { return IndexReference(sentence, token+ other); };
    
    std::string tostring() const {
        return std::to_string((unsigned int) sentence) + ":" + std::to_string((unsigned int) token);
    }
};

class IndexedData {
   public:
    std::vector<IndexReference> data;
    IndexedData() { };
    IndexedData(std::istream * in);
    void write(std::ostream * out) const; 
    
    bool has(const IndexReference & ref, bool sorted = false) const { 
        if (sorted) {
            return std::binary_search(this->begin(), this->end(), ref);
        } else {
            return std::find(this->begin(), this->end(), ref) != this->end();
        }
    }
    int count() const { return data.size(); }

    void insert(IndexReference ref) { data.push_back(ref); }
    size_t size() const { return data.size(); }

    typedef std::vector<IndexReference>::iterator iterator;
    typedef std::vector<IndexReference>::const_iterator const_iterator;
    
    iterator begin() { return data.begin(); }
    const_iterator begin() const { return data.begin(); }

    iterator end() { return data.end(); }
    const_iterator end() const { return data.end(); }

    iterator find(const IndexReference & ref) { return std::find(this->begin(), this->end(), ref); }
    const_iterator find(const IndexReference & ref) const { return std::find(this->begin(), this->end(), ref); }    

    std::set<int> sentences() const {
        std::set<int> sentences;
        for (const_iterator iter = this->begin(); iter != this->end(); iter++) {
            const IndexReference ref = *iter;
            sentences.insert(ref.sentence); 
        }
        return sentences;
    }

    std::set<IndexReference> set() const {
        return std::set<IndexReference>(this->begin(), this->end() );
    }

    void sort() {
        std::sort(this->begin(), this->end());
    }

    void reserve(size_t size) {
        data.reserve(size);
    }
    void shrink_to_fit() {
        data.shrink_to_fit();
    }

};

/************* ValueHandler for reading/serialising basic types ********************/


/*
 * Value handler deal are interfaces to the values in Pattern Maps. They are
 * used to abstract from the actual value data type and provide some common
 * methods required for all values, as well at methods for serialisation
 * from/to binary file. All are derived from the abstract class
 * AbstractValueHandler
*/

template<class ValueType>
class AbstractValueHandler {
   public:
    virtual std::string id() { return "AbstractValueHandler"; }
    virtual void read(std::istream * in, ValueType & value)=0; //read value from input stream (binary)
    virtual void write(std::ostream * out, ValueType & value)=0; //write value to output stream (binary)
    virtual std::string tostring(ValueType & value)=0; //convert value to string)
    virtual int count(ValueType & value) const =0; //what count does this value represent?
    virtual void add(ValueType * value, const IndexReference & ref ) const=0; //add the indexreference to the value, will be called whenever a token is found during pattern building

    virtual void convertto(ValueType * source, ValueType* & target ) const { target = source; }; //this doesn't really convert as source and target are same type, but it is required!
};

// This templated class can be used for all numeric base types (such as int, uint16_t,
// float, etc)
template<class ValueType>
class BaseValueHandler: public AbstractValueHandler<ValueType> {
   public:
    virtual std::string id() { return "BaseValueHandler"; }
    const static bool indexed = false;
    void read(std::istream * in, ValueType & v) {
        in->read( (char*) &v, sizeof(ValueType)); 
    }
    void write(std::ostream * out, ValueType & value) {
        out->write( (char*) &value, sizeof(ValueType));
    }
    virtual std::string tostring(ValueType & value) {
        return tostring(value);
    }
    int count(ValueType & value) const {
        return (int) value;
    }
    void add(ValueType * value, const IndexReference & ref ) const {
        *value = *value + 1;
    }

    void convertto(ValueType * source, ValueType* & target ) const { target = source; }; //this doesn't really convert as source and target are same type, but it is required!

    void convertto(ValueType * source, IndexedData* & target ) const { target = new IndexedData(); }; //this doesn't convert either, it returns a totally EMPTY indexeddata, allowing unindexed models to be read as indexed, but losing all counts!
};


/************* ValueHandler for reading/serialising indexed types ********************/


class IndexedDataHandler: public AbstractValueHandler<IndexedData> {
   public:
    const static bool indexed = true;
    virtual std::string id() { return "IndexedDataHandler"; }
    void read(std::istream * in, IndexedData & v) {
        uint32_t c;
        in->read((char*) &c, sizeof(uint32_t));
        v.reserve(c); //reserve space to optimise
        for (unsigned int i = 0; i < c; i++) {
            IndexReference ref = IndexReference(in);
            v.insert(ref);
        }
        v.shrink_to_fit(); //try to keep vector as small as possible (slows insertions down a bit)
    }
    void write(std::ostream * out, IndexedData & value) {
        const uint32_t c = value.count();
        out->write((char*) &c, sizeof(uint32_t));
        //we already assume everything is nicely sorted!
        for (IndexedData::iterator iter = value.data.begin(); iter != value.data.end(); iter++) {
            iter->write(out);
        }
    }
    virtual std::string tostring(IndexedData & value) {
        std::string s = "";
        for (IndexedData::iterator iter = value.data.begin(); iter != value.data.end(); iter++) {
            if (!s.empty()) s += " ";
            s += iter->tostring();
        }
        return s;
    }
    int count(IndexedData & value) const {
        return value.data.size();
    }
    void add(IndexedData * value, const IndexReference & ref ) const {
        if (value == NULL) {
            std::cerr << "ValueHandler: Value is NULL!" << std::endl;
            throw InternalError();
        }
        value->insert(ref);
    }
    void convertto(IndexedData * source , IndexedData *&  target) const { target = source;  }; //noop
    void convertto(IndexedData * value, unsigned int * & convertedvalue) const { convertedvalue = new unsigned int; *convertedvalue = (unsigned int) value->count(); };
};








template<class FeatureType>
class PatternFeatureVector {
    public:
        Pattern pattern;
        std::vector<FeatureType> data;

        PatternFeatureVector() {};
        virtual ~PatternFeatureVector() {};
        PatternFeatureVector(const Pattern & ref) { pattern = ref; }

        PatternFeatureVector(const Pattern & ref, const std::vector<FeatureType> & dataref) {
            pattern = ref;
            data = dataref;
        }

        //copy constructor
        PatternFeatureVector(const PatternFeatureVector & ref) {
            pattern = ref.pattern;
            data = ref.data;
        };
        PatternFeatureVector(std::istream * in) {
            read(in);
        }


        void read(std::istream * in) {
            this->pattern = Pattern(in);
            uint16_t c;
            in->read((char*) &c, sizeof(uint16_t));
            data.reserve(c);
            for (unsigned int i = 0; i < c; i++) {
                FeatureType f;
                in->read((char*) &f, sizeof(FeatureType));
                data.push_back(f);
            }
            data.shrink_to_fit();
        }
        void write(std::ostream * out) {
            this->pattern.write(out);
            unsigned int s = data.size();
            if (s >= 65536) {
                std::cerr << "ERROR: PatternFeatureVector size exceeds maximum 16-bit capacity!! Not writing arbitrary parts!!! Set thresholds to prevent this!" << std::endl;
                s = 65536;
            }
            uint16_t c = (uint16_t) s;
            out->write((char*) &c , sizeof(uint16_t));
            for (unsigned int i = 0; i < s; i++) {
                FeatureType f = data[i];
                out->write((char*) &f, sizeof(FeatureType));
            }
        }

        typedef typename std::vector<FeatureType>::iterator iterator;
        typedef typename std::vector<FeatureType>::const_iterator const_iterator;

        size_t size() const { return data.size(); }

        PatternFeatureVector<FeatureType>::iterator begin() { return data.begin(); }
        PatternFeatureVector<FeatureType>::const_iterator begin() const { return data.begin(); }

        PatternFeatureVector<FeatureType>::iterator end() { return data.end(); }
        PatternFeatureVector<FeatureType>::const_iterator end() const { return data.end(); }

        FeatureType get(int index) {
            return data[index];
        }

        void clear() {
            data.clear();
        }
        void push_back(FeatureType & f) {
            data.push_back(f);
        }
        void reserve(size_t size) {
            data.reserve(size);
        }
        void shrink_to_fit() {
            data.shrink_to_fit();
        }
         
};

template<class FeatureType>
class PatternFeatureVectorMap { //acts like a (small) map (but implemented as a vector to save memory), for 2nd-order use (i.e, within another map)
    public:


        std::vector<PatternFeatureVector<FeatureType> *> data;

        typedef typename std::vector<PatternFeatureVector<FeatureType>*>::const_iterator const_iterator;
        typedef typename std::vector<PatternFeatureVector<FeatureType>*>::iterator iterator;

        PatternFeatureVectorMap<FeatureType>() {};

        PatternFeatureVectorMap<FeatureType>(const PatternFeatureVectorMap<FeatureType> & ref) {
            for (const_iterator iter = ref.begin(); iter != ref.end(); iter++) {
                //make a copy
                const PatternFeatureVector<FeatureType> * pfv_ref = *iter;
                PatternFeatureVector<FeatureType> * pfv = new PatternFeatureVector<FeatureType>(*pfv_ref);
                this->data.push_back(pfv);
            }
        }


        /*   get double free or corruption error: //TODO: possible memory
         *   leak?? */
        virtual ~PatternFeatureVectorMap<FeatureType>() {
            /*
            const size_t s = this->data.size();
            for (int i = 0; i < s; i++) {
                PatternFeatureVector<FeatureType> * pfv = this->data[i];
                delete pfv;
                data[i] = NULL;
            }*/
        }

        bool has(const Pattern & ref) const { 
            for (const_iterator iter = this->begin(); iter != this->end(); iter++) {
                const PatternFeatureVector<FeatureType> * pfv = *iter;
                if (pfv->pattern == ref) {
                    return true;
                }
            }
            return false;
        }


       iterator find(const Pattern & ref) { 
            for (iterator iter = this->begin(); iter != this->end(); iter++) {
                const PatternFeatureVector<FeatureType> * pfv = *iter;
                if (pfv->pattern == ref) {
                    return iter;
                }
            }
            return this->end();
        }

        int count() const { return data.size(); }



        void insert(PatternFeatureVector<FeatureType> * pfv, bool checkexists=true) { 
            //inserts pointer directly, makes no copy!!
            if (checkexists) {
                iterator found = this->find(pfv->pattern);
                if (found != this->end()) {
                    const PatternFeatureVector<FeatureType> * old = *found;
                    delete old;
                    *found = pfv;
                } else {
                    this->data.push_back(pfv);
                }
            } else {
                this->data.push_back(pfv);
            }
        }

        void insert(PatternFeatureVector<FeatureType> & value, bool checkexists=true) { 
            //make a copy, safer
            PatternFeatureVector<FeatureType> * pfv = new PatternFeatureVector<FeatureType>(value);
            if (checkexists) {
                iterator found = this->find(value.pattern);
                if (found != this->end()) {
                    const PatternFeatureVector<FeatureType> * old = *found;
                    delete old;
                    *found = pfv;
                } else {
                    this->data.push_back(pfv);
                }
            } else {
                this->data.push_back(pfv);
            }
        }

        size_t size() const { return data.size(); }

        virtual std::string tostring() {
            //we have no classdecoder at this point
            std::cerr << "ERROR: PatternFeatureVector does not support serialisation to string" << std::endl;
            throw InternalError();
        }
        
        iterator begin() { return data.begin(); }
        const_iterator begin() const { return data.begin(); }

        iterator end() { return data.end(); }
        const_iterator end() const { return data.end(); }

        virtual PatternFeatureVector<FeatureType> * getdata(const Pattern & pattern) { 
            iterator iter = this->find(pattern);
            if (iter != this->end()) {
                PatternFeatureVector<FeatureType> * pfv = *iter;
                return pfv;
            }
            return NULL;
        }

        void reserve(size_t size) {
            data.reserve(size);
        }
        void shrink_to_fit() {
            data.shrink_to_fit();
        }


};

template<class FeatureType>
class PatternFeatureVectorMapHandler: public AbstractValueHandler<PatternFeatureVectorMap<FeatureType>> {
   public:
    virtual std::string id() { return "PatternFeatureVectorMapHandler"; }
    void read(std::istream * in, PatternFeatureVectorMap<FeatureType> & v) {
        uint16_t c;
        in->read((char*) &c, sizeof(uint16_t));
        v.reserve(c); //reserve space to optimise
        for (unsigned int i = 0; i < c; i++) {
            PatternFeatureVector<FeatureType> ref = PatternFeatureVector<FeatureType>(in);
            v.insert(ref, false); //checkifexists=false, to speed things up when loading, assuming data is sane
        }
        v.shrink_to_fit(); //try to keep vector as small as possible (slows additional insertions down a bit)

    }
    void write(std::ostream * out, PatternFeatureVectorMap<FeatureType> & value) {
        unsigned int s = value.size();
        if (s >= 65536) {
            std::cerr << "ERROR: PatternFeatureVector size exceeds maximum 16-bit capacity!! Not writing arbitrary parts!!! Set thresholds to prevent this!" << std::endl;
            s = 65535;
        }
        const uint16_t c = (uint16_t) s;
        out->write((char*) &c, sizeof(uint16_t));
        unsigned int n = 0;
        for (typename PatternFeatureVectorMap<FeatureType>::iterator iter = value.begin(); iter != value.end(); iter++) {
            if (n==s) break; 
            PatternFeatureVector<FeatureType> * pfv = *iter;
            pfv->write(out);
            n++;
        }
    }
    virtual std::string tostring(PatternFeatureVectorMap<FeatureType> & value) {
        std::cerr << "ERROR: PatternFeatureVectorMapHandler does not support serialisation to string (no classdecoder at this point)" << std::endl;
        throw InternalError();
    }
    int count(PatternFeatureVectorMap<FeatureType> & value) const {
        return value.size();
    }
    void add(PatternFeatureVectorMap<FeatureType> * value, const IndexReference & ref ) const {
        std::cerr << "ERROR: PatternFeatureVectorMapHandler does not support insertion of index references, model can not be computed with train()" << std::endl;
        throw InternalError();
    }
    void convertto(PatternFeatureVectorMap<FeatureType> * source , PatternFeatureVectorMap<FeatureType> * & target) const { target = source; }; //noop
    void convertto(PatternFeatureVectorMap<FeatureType> * source , IndexedData * & target) const { }; //not possible, noop (target = NULL)
    void convertto(PatternFeatureVectorMap<FeatureType> * value, unsigned int * & convertedvalue) const { convertedvalue = new unsigned int; *convertedvalue = value->count(); };
};

#endif
