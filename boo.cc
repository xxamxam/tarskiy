#include "boolstuff/BoolExprParser.h"
#include <assert.h>
#include <stdlib.h>
#include <stack>

#include <iostream>
#include <limits.h>
#include <set>
#include <stdio.h>
#include <string.h>
#include <string>
#include <sys/wait.h>
#include <unistd.h>
#include <vector>
#include <set>

using namespace std;
using namespace boolstuff;


bool reform(string & s, vector<string> & polynoms, vector<pair<int, int>> & poses, int left, int write){
    if(!(write>left)) return true;
    int s_itog = 0;
    int itog_pos_not = -1;
    int itog_pos_or = -1;
    int itog_pos_and = -1;
    bool vstr = false;
    for(int i = left; i < write; i++){
        if(s[i] == '(') ++s_itog;
        else if(s[i] == ')') --s_itog;
        else if(s_itog == 0){
            if(s[i] == '!') itog_pos_not = i;
            else if(s[i] == '&') itog_pos_and = i;
            else if(s[i] == '|') itog_pos_or = i; 
        }   
        if (s[i] == '!' or s[i] == '&' or s[i] == '|') vstr = true;
    }
    if(s_itog != 0){
        printf("Незакрытая скобка\n");
        return false;

    }

    if(itog_pos_or > 0){
        reform(s, polynoms, poses, left,itog_pos_or);
        reform(s, polynoms, poses, itog_pos_or+1, write);
    }
    else if (itog_pos_and > 0){
        reform(s, polynoms, poses, left, itog_pos_and);
        reform(s, polynoms, poses, itog_pos_and+1, write);

    }
    else if (itog_pos_not > 0){
        reform(s, polynoms, poses, left, itog_pos_not);
        reform(s, polynoms, poses, itog_pos_not + 1, write);

    }
    else{
        if(vstr) reform(s, polynoms, poses, left + 1, write - 1);
        else {
        poses.push_back({left,write-1});
        polynoms.push_back(s.substr(left + 1, write - left -2));
        }
        
    }
    return true;
}

string remove_probel(const string & s){
    string ss = "";
    size_t i = 0;
    while(s[i]!='\0') {
        if(s[i] != ' ') ss+=s[i];
        ++i;
    }
    return ss;
}

string reform_again(string & s, const vector<pair<int, int>>& poses){
    string ss = "";
    size_t i = 0;
    int num = 0;
    while(s[i] != '\0'){
        if(i == poses[num].first){
            ss += "a_" + to_string(num);
            i = poses[num++].second;
        } else ss +=s[i];
        ++i;
    }
    return ss; 
}

string count_perems(const string & s, set<char>& b){
    string rez = "";
    for(int i = 0; s[i] != '\0'; ++i)
        if(isalpha(s[i]) and b.find(s[i]) == b.end())
            rez += s[i], b.insert(s[i]);
    return rez;
}

int main(){
    BoolExprParser parser;
    string exist_perems = "";
    string perems = "";
    string line;
    while(true){
            cout<< "Введите переменные которые нужно убрать:\n";
            
            getline(cin, exist_perems);
            cout<< "Введите выражение:\n";
            if (!getline(cin,line)) break;
            try{
                set<char> used;
                exist_perems = remove_probel(exist_perems);
                for(int i = 0; exist_perems[i] != '\0'; ++i) used.insert(exist_perems[i]);
                perems = exist_perems + count_perems(line, used);
                vector<string> pol;
                vector<pair<int,int>> poses;

            
                line = remove_probel(line);
                

                if (!reform(line, pol, poses, 0 , line.size())) continue;
                line = reform_again(line, poses);

                BoolExpr<string> *expr = parser.parse(line);
                assert(expr != NULL); 
                BoolExpr<string> *dnf = BoolExpr<string>::getDisjunctiveNormalForm(expr);
                expr = NULL;
                stringstream ss;
                ss << dnf;
                string rez;
                ss >> rez;
                
 
                std::stringstream().swap(ss);
                int size = strlen(exist_perems.c_str());        
                ss << size;

                ss >> exist_perems;

                vector<char*> args;
                string name = "./next.py";
                string python = "python3";
                args.push_back((char*)python.c_str());
                args.push_back((char*)name.c_str());
                args.push_back((char*)(exist_perems.c_str()));
                args.push_back((char*)(perems.c_str()));
                args.push_back((char*)(rez.c_str()));

                for(int i = 0; i < pol.size(); ++i) args.push_back((char*)pol[i].c_str());
                args.push_back(nullptr);

                pid_t pid = fork();
                if(pid == 0){
            
                    int t = execvp(args[0], &args[0]);
                    if (t == -1) perror(args[0]);
                    return 0;
                } else if (pid> 0){
                    int status;
                    pid = waitpid(pid, &status, 0);
                    if (status != 0) {
                    perror("ошибка");
                    }
                } else{
                    cout<<"вычисление не запустилось\n";
                }

            }
             catch (BoolExprParser::Error &err)
        {
            cout << "Error #" << err.code << " at character #" << err.index << endl;
        }

          
    }

}
