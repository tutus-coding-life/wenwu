import pandas as pd
columns=['Name','Category','Dynasty','Image','MotifAndPattern','ObjectType','FormAndStructure']
def write(output_file,df):
    df.to_excel(output_file, index=False)
    print(f"Data written to {output_file}")

def main():
    df_ceramic = pd.DataFrame(columns=columns)
    df_Bronze = pd.DataFrame(columns=columns)
    df_Lacquer = pd.DataFrame(columns=columns)
    df = pd.read_excel('./data/testt.xlsx')
    num1,num2,num3=0,0,0
    for i in range(1,len(df)):
        if(num1>30 and num2>30 and num3>30) :break
        x = df.loc[i,'Category']
        x1,x2,x3=pd.isnull(df.loc[i,'MotifAndPattern']),pd.isnull(df.loc[i,'ObjectType']),pd.isnull(df.loc[i,'FormAndStructure'])
        if  x1==False and x2==False and x3==False:
            if  x == 'Ceramics' :
                df_ceramic.loc[len(df_ceramic)] = df.loc[i]
                num1+=1
            elif x=='Bronze, Brass, and Copper':
                df_Bronze.loc[len(df_Bronze)] = df.loc[i]
                num2+=1
            elif x=='Lacquer':
                df_Lacquer.loc[len(df_Lacquer)] = df.loc[i]
                num3+=1

    write('./data/ceramic_tag.xlsx',df_ceramic)
    write('./data/Bronze_tag.xlsx',df_Bronze)
    write('./data/Lacquer_tag.xlsx',df_Lacquer)

if __name__ == '__main__':
    main()