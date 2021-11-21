#include "boolstuff/BoolExprParser.h"
#include <assert.h>
#include <stdlib.h>
#include <stack>

#include <dirent.h>
#include <fcntl.h>
#include <iostream>
#include <limits.h>
#include <set>
#include <stdio.h>
#include <string.h>
#include <string>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <vector>
#include <signal.h>
#include <sys/resource.h>
#include <time.h>
#include <signal.h>

using namespace std;
using namespace boolstuff;


bool reform(string & s, vector<string> & polynoms, vector<pair<int, int>> & poses, int left, int write){
    if(!(write>left)) return true;
    int s_itog = 0, itog_pos = -1;
    for(int i = left; i < write; i++){
        if(s[i] == '(') ++s_itog;
        else if(s[i] == ')') --s_itog;
        if(s[i] == '!' or s[i] == '&' or s[i] == '|'){
            if (s_itog == 1) itog_pos = i;
        }   
    }
    if(s_itog != 0){
        printf("Незакрытая скобка\n");
        return false;

    }
    if(itog_pos > 0){
            reform(s, polynoms, poses, left+1,itog_pos);
            reform(s, polynoms, poses, itog_pos+1, write - 1);
    }
    else{
        poses.push_back({left,write-1});
        polynoms.push_back(s.substr(left + 1, write - left -2));
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

int main(){
    BoolExprParser parser;
    string line;
    while(getline(cin,line)){
            try{
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
                string rez = ss.str();


            vector<char*> args;
            string name = "./next.py";
            string python = "python3";
            args.push_back((char*)python.c_str());
            args.push_back((char*)name.c_str());
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