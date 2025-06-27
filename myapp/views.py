import datetime
from django.shortcuts import render
from django.shortcuts import render, redirect
from .forms import CSVFileUploadForm1
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.template import loader
from django.http import HttpResponse
from dateutil.parser import parse
import pandas as pd
import numpy as np
import json
import pyarrow.csv as pc
import pandas as pd
from datetime import datetime

entries1 = 0
entries2 = 0
entries3 = 0
entries4 = 0
entries5 = 0
entries6 = 0
entries7 = 0
entries8 = 0

claim_entries1 = 0
claim_entries2 = 0
claim_entries3 = 0
claim_entries = 0

os_entries1 = 0
os_entries2 = 0
os_entries3 = 0


column = ''
def os_file_upload(request):
    message = ""
    columns = []
    is_merged = False
    file_details = []  # List to store file names and number of entries
    total_entries = 0  # Variable to store the total number of entries across all files

    if request.method == 'POST':
        form = CSVFileUploadForm1(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('files')
            dataframes = []
            
            for file in files:
                df = pd.read_csv(file)
                num_entries = len(df)
                total_entries += num_entries  # Add to total entries
                file_details.append({'name': file.name, 'entries': num_entries})
                dataframes.append(df)

            merged_df = pd.concat(dataframes)
            merged_df['empty'] = None
            # Convert the merged DataFrame to JSON and store it in the session
            request.session['merged_df'] = merged_df.to_json(orient='split')
            message = "Files Merged Successfully"
            is_merged = True
            # Store the column names in the session
            request.session['merged_columns'] = merged_df.columns.tolist()
            columns = merged_df.columns.tolist()

    else:
        form = CSVFileUploadForm1()

    return render(request, 'myapp/os_page.html', {
        'form': form,
        'message': message,
        'is_merged': is_merged,
        'columns': columns,
        'file_details': file_details,  # Pass the file details to the template
        'total_entries': total_entries  # Pass the total entries to the template
    })

# Your utility functions
def convert_numpy(obj):
    if isinstance(obj, np.generic):
        return obj.item()  # np.generic includes np.int64, np.float64 and more
    elif isinstance(obj, dict):
        return {k: convert_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy(v) for v in obj]
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj

def store_results_in_session(request, key, results):
    #print(f"Storing data for key: {key}")  # Debug print
    request.session[key] = results

def get_results_from_session(request, key):
    data = request.session.get(key)
    #print(f"Retrieving data for key: {key}, Data: {data}")  # Debug print
    return data

def clear_results_from_session(request, key):
    if key in request.session:
        del request.session[key]



def process_os_data(request):
    received_format = request.POST.get('date_format')    
    translated_format = translate_format11(received_format)
    print("hello world")
    # Check if the 'merged_df' key exists in the session
    if 'merged_df' in request.session:
        # Retrieve the merged DataFrame from the session
        merged_df_json = request.session['merged_df']
        merged_df = pd.read_json(merged_df_json, orient='split')
        print("Here is merged", merged_df.head())
    else:
        return HttpResponse("Merged DataFrame not found in session.", status=400)
    

    # Process the DataFrame based on the user's input
    if request.method == 'POST':
        print("check1")
        # Determine if 'Yes' was selected for claimId availability
        selected_values = request.session.get('selectedValues', [])
        claimId_available = request.POST.get('claimId_available') == 'yes'
        if selected_values is not None and selected_values:
            uid_column = 'UID'
            merged_df['UID'] = merged_df[selected_values].astype(str).agg('-'.join, axis=1)
            print("Selected values",selected_values)
            print("column is",merged_df[uid_column])
        else:
            uid_column = request.POST.get('UID')
            print("UID COL IS",uid_column)

        # uid_column = request.POST.get('UID')
        loss_date_column = request.POST.get('LOSS_DATE')
        claim_type_column = request.POST.get('CLAIM_TYPE')
        #claim_amount_column = request.POST.get('CLAIM_AMOUNT')
        AsAtDate = request.POST.get('AsAtDate')


        AsAtDate_Selection = request.POST.get('showSection')
        print("AsAtDate selection is",AsAtDate)
        selected_value = request.POST.get('selected_value') #selected value for AsAtDate
        print("column is ",column)  #Selected column for AsAtDate
        print("Value is",selected_value)

        if AsAtDate_Selection =='yes':
            merged_df = merged_df[merged_df[column] == selected_value]
            print("After AsAtDate removal is",merged_df[column])
            
        
        print("2 merged", merged_df.head())
        
        
        null_lossDate1 = merged_df[loss_date_column].isnull()
        null_entries_df1 = merged_df[null_lossDate1]
        null_lossDate_df1 = pd.DataFrame(null_entries_df1)
    
        #print("Translated format:", translated_format)
        print("Before conversion***************************************************")
        print(merged_df[loss_date_column])
        merged_df[loss_date_column] = merged_df[loss_date_column].apply(lambda x: try_parsing_date11(x,translated_format))
        print("AFTER  conversion***************************************************")
        print(merged_df[loss_date_column])
        print("********************************************************************")
        print("3 merged", merged_df.head())

        # merged_df[payment_column] = pd.to_datetime(
        #     merged_df[payment_column],format=translated_format, errors='coerce'
        #     )



        print("4 merged", merged_df.head())
        print("*****************************")

        print("**********************")
        print('TOTAL DF',merged_df.head())
        print("UID COMING",uid_column)

        print("UID",merged_df['UID'].head())
        print("LossDate",merged_df[loss_date_column].head())
        print("ClaimType",merged_df[claim_type_column].head())


        

        claim_id_column = request.POST.get('CLAIMID')
        if claimId_available:
            claim_amount_column11 = request.POST.get('CLAIM_AMOUNT1')
            operator = request.POST.get('OPERATOR1')
            claim_amount_column22 = request.POST.get('CLAIM_AMOUNT2')
            print("CLaim amount 1",claim_amount_column11)
            print("CLaim amount 2",claim_amount_column22)
            print("OPT",operator)
            merged_df[claim_amount_column11] = pd.to_numeric(merged_df[claim_amount_column11], errors='coerce')
            merged_df[claim_amount_column22] = pd.to_numeric(merged_df[claim_amount_column22], errors='coerce')
            
            if (claim_amount_column11 is None) and (claim_amount_column22 is None):
                print("hello")
                claim_amount_column=claim_amount_column11
            elif (claim_amount_column22=='empty'):
                claim_amount_column=claim_amount_column11
            else:
                if operator=='+':
                    # Calculate the total claim paid
                    merged_df['Claim Paid'] = merged_df[claim_amount_column11] + merged_df[claim_amount_column22]
                    print("hello 11")
                    #merged_df['Claim Paid']= merged_df[claim_amount_column11]+merged_df[claim_amount_column22]
                    print(merged_df['Claim Paid'])
                elif operator=='-':
                    print("hello")
                    merged_df['Claim Paid']= merged_df[claim_amount_column11]-merged_df[claim_amount_column22] 
                claim_amount_column='Claim Paid'
            
            # Claim_df = merged_df.groupby(['UID',claim_type_column,loss_date_column]).agg({
            #     claim_amount_column: 'sum',
            # }).reset_index()
            No_Claim_df = merged_df.groupby([uid_column,claim_id_column,claim_type_column,loss_date_column]).agg({
                claim_amount_column: 'sum',
            }).reset_index()
            No_Claim_df.columns = ['UID','ClaimId', 'ClaimType', 'LossDate', 'OsPaid']
        else:
            claim_amount_column11 = request.POST.get('CLAIM_AMOUNT1')
            operator = request.POST.get('OPERATOR1')
            claim_amount_column22 = request.POST.get('CLAIM_AMOUNT2')
            print("CLaim amount 1",claim_amount_column11)
            print("CLaim amount 2",claim_amount_column22)
            print("OPT",operator)
            merged_df[claim_amount_column11] = pd.to_numeric(merged_df[claim_amount_column11], errors='coerce')
            merged_df[claim_amount_column22] = pd.to_numeric(merged_df[claim_amount_column22], errors='coerce')
            
            if (claim_amount_column11 is None) and (claim_amount_column22 is None ):
                print("hello")
                claim_amount_column=claim_amount_column11
            elif (claim_amount_column22=='empty'):
                claim_amount_column=claim_amount_column11
            else:
                if operator=='+':
                    # Calculate the total claim paid
                    merged_df['Claim Paid'] = merged_df[claim_amount_column11] + merged_df[claim_amount_column22]
                    print("hello 11")
                    #merged_df['Claim Paid']= merged_df[claim_amount_column11] + merged_df[claim_amount_column22]
                    print(merged_df['Claim Paid'])
                elif operator=='-':
                    print("hello")
                    merged_df['Claim Paid']= merged_df[claim_amount_column11]-merged_df[claim_amount_column22] 
                claim_amount_column='Claim Paid'
            
            Claim_df = merged_df.groupby(['UID',claim_type_column,loss_date_column]).agg({
                claim_amount_column: 'sum',
            }).reset_index()
            No_Claim_df= merged_df.groupby(['UID', loss_date_column,claim_type_column])[claim_amount_column].sum().reset_index()
            No_Claim_df.columns = ['UID', 'LossDate','ClaimType', 'OsPaid']
        
        df_display=No_Claim_df


        print("converted claims data",No_Claim_df)


        print("This is not_claim_df",No_Claim_df.head())
        print("check4")

        claims_data = request.session.get('No_Claim_df')

        if claims_data:
            if claimId_available:
                claims_data = pd.read_json(claims_data, orient='split')

                print("check 88")
                print("**************************************")
                print(claims_data.head())
                print("**************************************")
                claims_data.columns = ['UID','ClaimId', 'ClaimType', 'LossDate', 'ClaimPaid']
                claims_data['LossDate'] = pd.to_datetime(claims_data['LossDate'], unit='ms')
                print("check 90")
                print("**************************************")
                print(claims_data.head())
                print("**************************************")


                claims_data['UID'] = claims_data['UID'].astype(str)
                No_Claim_df['UID'] = No_Claim_df['UID'].astype(str)
                claims_data['ClaimId'] = claims_data['ClaimId'].astype(str)
                No_Claim_df['ClaimId'] = No_Claim_df['ClaimId'].astype(str)
                claims_data['LossDate'] = claims_data['LossDate'].astype(str)
                No_Claim_df['LossDate'] = No_Claim_df['LossDate'].astype(str)
                claims_data['ClaimType'] = claims_data['ClaimType'].astype(str)
                No_Claim_df['ClaimType'] = No_Claim_df['ClaimType'].astype(str)
            else:
                claims_data = pd.read_json(claims_data, orient='split')
                claims_data.columns = ['UID', 'LossDate','ClaimType', 'ClaimPaid']
                claims_data['UID'] = claims_data['UID'].astype(str)
                No_Claim_df['UID'] = No_Claim_df['UID'].astype(str)
                claims_data['LossDate'] = claims_data['LossDate'].astype(str)
                No_Claim_df['LossDate'] = No_Claim_df['LossDate'].astype(str)
                claims_data['ClaimType'] = claims_data['ClaimType'].astype(str)
                No_Claim_df['ClaimType'] = No_Claim_df['ClaimType'].astype(str)
        else:
            claims_data=pd.DataFrame()        

            print("Both data")
            print(claims_data)
            print(No_Claim_df)

        if not claims_data.empty:
            print("data of claims ",claims_data.head())
            print("data of Os ",No_Claim_df.head())
            #outter = pd.merge(claims_data, No_Claim_df, on=['UID','LossDate','ClaimType'], how='outer')
            # if not 'ClaimType' in claims_data:
            if 'ClaimType' in claims_data.columns:
                if claimId_available:
                    outter = pd.merge(claims_data, No_Claim_df, on=['UID','ClaimId', 'ClaimType', 'LossDate'], how='outer')
                else:
                    outter = pd.merge(claims_data, No_Claim_df, on=['UID', 'LossDate', 'ClaimType'], how='outer')
            else:
                No_Claim_df2= No_Claim_df.groupby(['UID', loss_date_column])[claim_amount_column].sum().reset_index()
                outter = pd.merge(claims_data, No_Claim_df2, on=['UID', 'LossDate'], how='outer')

            print("Outter data is ",outter.head())
            outter['ClaimPaid'].fillna(0, inplace=True)
            outter['OsPaid'].fillna(0, inplace=True)
            outter['ClaimPaid'] = pd.to_numeric(outter['ClaimPaid'], errors='coerce')
            outter['OsPaid'] = pd.to_numeric(outter['OsPaid'], errors='coerce')
            outter['ReportedClaim'] = outter['ClaimPaid'] + outter['OsPaid']
            negative_reported_claims = outter[outter['ReportedClaim'] <= 0]
            print("Reported Claims data is ",outter.head())
        else:
            outter=pd.DataFrame()
        
        
        outter1 = outter.copy() 
        check_df = outter1
        if not claims_data.empty:
            check_df['LossDate'] = check_df['LossDate'].astype(str)
            #check_df['LossDate'] = check_df['LossDate'].dt.strftime(translated_format)
        claim_amounts_df = No_Claim_df.copy()

        # Convert the ClaimAmount_SUM column to numeric, setting errors to NaN
        claim_amounts_df['OsPaid'] = pd.to_numeric(claim_amounts_df['OsPaid'], errors='coerce')
        nan_count_before = claim_amounts_df['OsPaid'].isna().sum()

        # Drop NaN values that resulted from the conversion
        claim_amounts_df.dropna(inplace=True)

        os_entries1=nan_count_before

        # Filter the DataFrame to only contain negative values
        negative_claims_df = claim_amounts_df[claim_amounts_df['OsPaid'] < 0]

        # Count the number of negative ClaimAmount_SUM entries
        negative_claims_count = negative_claims_df['OsPaid'].count()

        print(f"The count of negative OsPaid entries is: {negative_claims_count}")

        
        # try:
        #         original_count = len(merged_df)
        #         print(original_count)
        #         print(outter.shape)
        #         outter['LossDate'] = pd.to_datetime(
        #             outter['LossDate'],
        #             format=translated_format, errors='coerce'
        #             #errors='coerce'  # This will replace non-parsable dates with NaT
        #         )
        #         # Drop rows where dates could not be parsed
        #         print("Check end entries before",outter['LossDate'])
        #         #merged_df.dropna(subset=[loss_date_column], inplace=True)
        #         final_count = len(outter)
        #         entries2 = original_count - final_count
        #         # print("Enrties removed due to Date conversion of edorsement ",entries2)
        #         print(f"Total entries: {original_count}")
        #         # print(f"Removed entries: {removed_count}")
        #         print(f"Total after removal: {final_count}")
        #         print("Check end entries After",outter['LossDate'])
        # except ValueError as e:
        #     print(f"There was an issue with the date format: {e}")

        outter['LossDate'] = outter['LossDate'].apply(lambda x: try_parsing_date11(x, translated_format))
        original_count = len(merged_df)
        print(original_count)
        final_count = len(outter)
        entries2 = original_count - final_count
        # print("Enrties removed due to Date conversion of edorsement ",entries2)
        print(f"Total entries: {original_count}")
        # print(f"Removed entries: {removed_count}")
        print(f"Total after removal: {final_count}")
        print("Check end entries After",outter['LossDate'])

        #selected_split = request.POST.get('split_type')
        selected_split = request.session.get('report_type')
        print("THE VALUE OF REPORT TYPPE IS *******************************************************",selected_split)

        if selected_split == 'Yearly':
            print("Selected SPLIT TYPE YEARLY")
            outter['Period'] = outter['LossDate'].dt.year
        elif selected_split == 'Quarterly':
            print("Selected SPLIT TYPE QUARTERLY ")
            # outter['Period'] = outter['LossDate'].apply(lambda x: f"Q{x.quarter} {x.year}")
            outter['Period'] = pd.to_datetime(outter['LossDate']).apply(lambda x: f"Q{x.quarter} {x.year}")
            
        outter['claim_count'] = 1



        # No_Claim_df['period'] = No_Claim_df['LossDate'].dt.year
        # Assuming 'No_Claim_df' is your DataFrame
        print("No_Claim",No_Claim_df.head())
        # Store the DataFrame in the session for download




        # Group by 'UID' and 'Period', and then calculate the sum of 'claim_count' and 'ClaimAmount_SUM'
        # grouped_df = outter.groupby(['UID', 'Period']).agg({
        #     'claim_count': 'sum',
        #     'OSPaid': 'sum'
        # }).reset_index()

        # print("this is grouped_df",grouped_df.head())

        
        
        
        consol = outter
        # No_Claim_df.drop(['Period', 'claim_count'], axis=1, inplace=True)
        outter['LossDate'] = outter['LossDate'].dt.strftime(translated_format)

        # The grouped_df DataFrame now contains the sum of 'claim_count' and 'ClaimAmount_SUM' for each combination of 'UID' and 'Period'


        #new_df_json = request.session.get('new_df')
        new_df_json = request.session.get('mapping_data_final')
        if not new_df_json:  # Check if new_df_json is empty
            new_df_json = request.session.get('new_df')



        # Quarter Data Groupby
        # Quarter_data_json = request.session.get('Quarter_df')
        


        # print("new DF is 0",new_df.head())
        
        if new_df_json:
            new_df = pd.read_json(new_df_json, orient='split')
            print("New DF head",new_df.head())
            print("Consol DF head",consol.head())
            consol['UID'] = consol['UID'].astype(str)
            consol['Period'] = consol['Period'].astype(str)
            new_df['UID'] = new_df['UID'].astype(str)
            new_df['Period'] = new_df['Period'].astype(str)
        else:
            # Handle the case where new_df is not in the session
            new_df = pd.DataFrame()  # or handle this scenario appropriately


        # orphan_uids = []
        # print("orphanorphan")
        if not new_df.empty:
            result_df = new_df.merge(consol, on=['UID', 'Period'], how='left') #new_df is premium and consol is claims
            result_df['claim_count'] = result_df['claim_count'].fillna(0)
            orphan_mask = (result_df['claim_count'] == 0)
            # print("orphan")
            # print(orphan_mask)

            # # Extract the UIDs and Periods of the orphan claims
            orphan_claims = result_df.loc[orphan_mask, ['UID', 'Period']]
            # print("orphan")
            # print(orphan_claims)
            # # If you only need the IDs (UIDs) as a list, you can extract them like this:
            orphan_uids = orphan_claims['UID'].unique().tolist()
            orphan_uids=pd.DataFrame(orphan_uids, columns=['UID'])
            orphan_uids = result_df[orphan_mask]
            # print("Orphan Claims")
            # print(orphan_uids)
        else:
            result_df = pd.DataFrame()  # or handle this scenario appropriately

        
        # print("Orphan Claims")
        # print(orphan_uids)
            
        request.session['orphan_uids'] = orphan_uids.to_json(orient='split')
        # orphan_uids_html = orphan_uids.head().to_html(classes='dataframe', index=False, escape=False)
        # Replace 'Column1', 'Column2', etc. with actual column names from new_df
        # result_df = result_df.dropna(subset=['UID', 'Period'])
        # print("Successful matches:\n", result_df)
            

        def convert_to_date(value):
            try:
                numeric_value = pd.to_numeric(value)
                return pd.to_datetime(numeric_value, unit='ms').strftime('%d-%m-%Y')
            except ValueError:
                return 'Invalid Date'

    # Assuming `check_df` is your DataFrame with the 'lossdate' column
        



    # Store the DataFrame in the session for download
        if not claims_data.empty:
            request.session['check_df'] = check_df.to_json(orient='split')
            # check_df['LossDate'] = pd.to_datetime(
            # check_df['LossDate'],format=translated_format, errors='coerce'
            # )
            # check_df['LossDate'] = check_df['LossDate'].dt.strftime(translated_format)
            #check_df['LossDate'] = check_df['LossDate'].apply(convert_to_date)
        request.session['result_df'] = result_df.to_json(orient='split')
        request.session['result_df1'] = result_df.to_json(orient='split')
        result_df_formatted = result_df.head().copy()

        if not new_df.empty:
            result_df_formatted['Exposure'] = result_df_formatted['Exposure'].round(3)
            result_df_formatted['UID_expsoure'] = result_df_formatted['UID_expsoure'].round(3)
            result_df_formatted['Gross Premium_SUM'] = result_df_formatted['Gross Premium_SUM'].round(0)
            #result_df_formatted['sum_Insured'] = result_df_formatted['sum_Insured'].round(0)
            result_df_formatted['EarnedPremium'] = result_df_formatted['EarnedPremium'].round(0)
        consol = result_df_formatted.head().to_html(classes='dataframe', index=False, escape=False)
        request.session['download_df'] = df_display.to_json(orient='split')

        #grouped_df_html = grouped_df.to_html(classes='dataframe', index=False, escape=False)



        result_df_html = result_df.to_html(classes='dataframe', index=False, escape=False)
        check_df1 = pd.read_json(request.session.get('check_df', '{}'), orient='split')
        result_df1 = pd.read_json(request.session.get('result_df', '{}'), orient='split')

        request.session['null_lossDate_df1'] = null_lossDate_df1.to_json(orient='split')
        request.session['negative_reported_claims'] = negative_reported_claims.to_json(orient='split')

        null_lossDate_df1_len = len(null_lossDate_df1)
        negative_reported_claims_len = len(negative_reported_claims)
        orphan_uids_len = len(orphan_uids)



        results = {
            'df_html': df_display.head().to_html(classes='dataframe', index=False, escape=False),
            'grouped_df_html': check_df.head().to_html(classes='dataframe', index=False, escape=False),
            'new_df_html': consol,
            'download_ready': True,
            # 'check_result': check_df1.to_dict('records') if isinstance(check_df1, pd.DataFrame) else check_df1,  # Convert DataFrame to list of dicts
            # 'result_result': result_df1.to_dict('records') if isinstance(result_df1, pd.DataFrame) else result_df1,  # Convert DataFrame to list of dicts
            #'BlankPDate':null_payment.head().to_html(classes='dataframe', index=False, escape=False),
            'null_lossDate_df1': null_lossDate_df1.head().to_html(classes='dataframe', index=False, escape=False),
            'negative_reported_claims':negative_reported_claims.head().to_html(classes='dataframe', index=False, escape=False),
            'null_lossDate_df1_len':null_lossDate_df1_len,
            'negative_reported_claims_len':negative_reported_claims_len,
            'orphan_uids': orphan_uids.head().to_html(classes='dataframe', index=False, escape=False) if isinstance(orphan_uids, pd.DataFrame) else orphan_uids,
            'orphan_uids_len':orphan_uids_len
        }
        
        serializable_results = convert_numpy(results)

        # Store the serializable results in the session
        store_results_in_session(request, 'os_results', serializable_results)

        # Redirect to the display view
        return redirect('display_os_results')

        #return render(request, 'myapp/osData.html', context)
    else:
        # Handle the case where method is not POST
        # For example, redirect to the home page or show an error message
        return HttpResponse("Invalid request.", status=400)


def display_os_results(request):
    results = get_results_from_session(request, 'os_results')
    if results is None:
        return HttpResponse("No results available. Please go through the processing step first.")
    return render(request, 'myapp/osData.html', results)




def claims_file_upload(request):
    message = ""
    columns = []
    is_merged = False
    file_details = []  # List to store file names and number of entries
    total_entries = 0  # Variable to store the total number of entries across all files

    if request.method == 'POST':
        form = CSVFileUploadForm1(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('files')
            dataframes = []
            
            for file in files:
                df = pd.read_csv(file)
                num_entries = len(df)
                total_entries += num_entries  # Add to total entries
                file_details.append({'name': file.name, 'entries': num_entries})
                dataframes.append(df)

            merged_df = pd.concat(dataframes)
            merged_df['empty'] = None
            # Convert the merged DataFrame to JSON and store it in the session
            request.session['merged_df'] = merged_df.to_json(orient='split')
            message = "Files Merged Successfully"
            is_merged = True
            # Store the column names in the session
            request.session['merged_columns'] = merged_df.columns.tolist()
            columns = merged_df.columns.tolist()

    else:
        form = CSVFileUploadForm1()

    return render(request, 'myapp/claims.html', {
        'form': form,
        'message': message,
        'is_merged': is_merged,
        'columns': columns,
        'file_details': file_details,  # Pass the file details to the template
        'total_entries': total_entries  # Pass the total entries to the template
    })




def process_claims_data(request):
    received_format = request.POST.get('date_format')
    translated_format = translate_format11(received_format)
    orphan_uids = pd.DataFrame()
    print("hello world")
    # Check if the 'merged_df' key exists in the session
    selected_values = request.session.get('selectedValues', [])
    print("Selected values are",selected_values)
    if 'merged_df' in request.session:
        # Retrieve the merged DataFrame from the session
        merged_df_json = request.session['merged_df']
        merged_df = pd.read_json(merged_df_json, orient='split')
        print("Here is merged", merged_df.head())
    else:
        return HttpResponse("Merged DataFrame not found in session.", status=400)
    

    print("aelected**********",selected_values)

    
    



    # Process the DataFrame based on the user's input
    if request.method == 'POST':
        print("check1")
        # Determine if 'Yes' was selected for claimId availability
        total_entries=len(merged_df)
        # startD=try_parsing_date(request.POST.get('startDate'))
        # endD = try_parsing_date(request.POST.get('endDate'))
        claimId_available = request.POST.get('claimId_available') == 'yes'
        if selected_values is not None and selected_values:
            uid_column = 'UID'
            merged_df['UID'] = merged_df[selected_values].astype(str).agg('-'.join, axis=1)
            print("Selected values",selected_values)
            print("column is",merged_df[uid_column])
        else:
            uid_column = request.POST.get('UID')
            print("UID COL IS",uid_column)

        #uid_column = request.POST.get('UID')
        loss_date_column = request.POST.get('LOSS_DATE')
        claim_type_column = request.POST.get('CLAIM_TYPE')
        claim_amount_column = request.POST.get('CLAIM_AMOUNT')
        list1 = ['Amount1','Amount2','Amount3']
        
        
        
        # print("Initial")
        # print("UID",uid_column)
        # print("Loss Date",loss_date_column)
        # print("Claim Type",claim_type_column)
        # print("Claim Amount",claim_amount_column)
        

        
        if claimId_available:
            print("check2")
            claim_id_column1 = request.POST.get('CLAIMID')
            # Group by ClaimId and ClaimType
            if selected_values is not None and selected_values:
                uid_column1 = 'UID'
                merged_df['UID'] = merged_df[selected_values].astype(str).agg('-'.join, axis=1)
                print("Selected values",selected_values)
                print("column is",merged_df['UID'])
            else:
                uid_column1 = request.POST.get('UID1')

                print("UID COL IS",uid_column1)
        

            #uid_column1 = request.POST.get('UID1')
            lossDate = request.POST.get('LOSS_DATE1')
            claim_type_column1 = request.POST.get('CLAIM_TYPE1')
            claim_amount_column1 = request.POST.get('CLAIM_AMOUNT1')


            # print("Translated format:", translated_format)
            merged_df[lossDate] = merged_df[lossDate].apply(lambda x: try_parsing_date11(x,translated_format))
            print(merged_df.at[0, lossDate])
            # merged_df = merged_df[(merged_df[lossDate] >= startD) & (merged_df[lossDate] <= endD)]
            # print(startD)
            # print(endD)
            print('loss_date_filter**********************')
            print(merged_df)


            null_lossDate = merged_df[lossDate].isnull()
            null_entries_df = merged_df[null_lossDate]
            null_lossDate_df = pd.DataFrame(null_entries_df)    

            one_to_one = merged_df.groupby(claim_id_column1).filter(lambda x: x[lossDate].nunique() > 1)
    

            print("1 merged", merged_df.head())
            
            print("type is ",merged_df[lossDate].dtype)

            # Claim_df = merged_df.groupby([claim_id_column1, claim_type_column1]).agg({
            #     uid_column1: 'last',
            #     lossDate: 'max',
            #     claim_amount_column1: 'sum',
            # }).reset_index()
            
            claim_amount_column11 = request.POST.get('CLAIM_AMOUNT11')
            operator = request.POST.get('OPERATOR')
            claim_amount_column22 = request.POST.get('CLAIM_AMOUNT22')
            print("CLaim amount 1",claim_amount_column11)
            print("CLaim amount 2",claim_amount_column22)
            print("OPT",operator)
            merged_df[claim_amount_column11] = pd.to_numeric(merged_df[claim_amount_column11], errors='coerce')
            merged_df[claim_amount_column22] = pd.to_numeric(merged_df[claim_amount_column22], errors='coerce')
            
            if (claim_amount_column11 is None) and (claim_amount_column22 is None):
                print("hello")
                claim_amount_column1=claim_amount_column11
            elif (claim_amount_column22=='empty'):
                claim_amount_column1=claim_amount_column11
            else:
                if operator=='+':
                    # Calculate the total claim paid
                    merged_df['Claim Paid'] = merged_df[claim_amount_column11] + merged_df[claim_amount_column22]
                    print("hello 11")
                    #merged_df['Claim Paid']= merged_df[claim_amount_column11]+merged_df[claim_amount_column22]
                    print(merged_df['Claim Paid'])
                elif operator=='-':
                    print("hello")
                    merged_df['Claim Paid']= merged_df[claim_amount_column11]-merged_df[claim_amount_column22] 
                claim_amount_column1='Claim Paid'
            
            print(merged_df.columns)
            Claim_df = merged_df.groupby([uid_column1,claim_id_column1,claim_type_column1,lossDate]).agg({
                claim_amount_column1: 'sum',
            }).reset_index()
            
            print(merged_df)
            Claim_df.columns = ['UID','ClaimId', 'ClaimType', 'LossDate', 'ClaimPaid']
            #Claim_df['LossDate'] = Claim_df['LossDate'].dt.strftime(translated_format)

            request.session['No_Claim_df'] = Claim_df.to_json(orient='split')

            claim_amounts_df = Claim_df.copy()

            # Convert the ClaimAmount_SUM column to numeric, setting errors to NaN
            claim_amounts_df['ClaimPaid'] = pd.to_numeric(claim_amounts_df['ClaimPaid'], errors='coerce')

            nan_count_before = claim_amounts_df['ClaimPaid'].isna().sum()

            # Drop NaN values that resulted from the conversion
            claim_amounts_df.dropna(subset=['ClaimPaid'], inplace=True)
            
            claim_entries1=nan_count_before

            total_after = claim_amounts_df.shape[0]


            # Filter the DataFrame to only contain negative values in 'ClaimPaid'
            negative_claims_df = claim_amounts_df[claim_amounts_df['ClaimPaid'] < 0]
            print(negative_claims_df)
            # Count the number of negative ClaimAmount_SUM entries
            negative_claims_count = negative_claims_df['ClaimPaid'].count()

            print(f"The count of negative ClaimAmount_SUM entries is: {negative_claims_count}")

            Claim_df['LossDate'] = Claim_df['LossDate'].apply(lambda x: try_parsing_date11(x,translated_format))
            
            
            # try:
            #         original_count = len(merged_df)
            #         print(original_count)
            #         print(Claim_df.shape)
            #         Claim_df['LossDate'] = pd.to_datetime(
            #             Claim_df['LossDate'],
            #             format=translated_format, errors='coerce'
            #             #errors='coerce'  # This will replace non-parsable dates with NaT
            #         )
            #         # Drop rows where dates could not be parsed
            #         print("Check end entries before",Claim_df['LossDate'])
            #         #merged_df.dropna(subset=[loss_date_column], inplace=True)
            #         final_count = len(Claim_df)
            #         entries2 = original_count - final_count
            #         # print("Enrties removed due to Date conversion of edorsement ",entries2)
            #         print(f"Total entries: {original_count}")
            #         # print(f"Removed entries: {removed_count}")
            #         print(f"Total after removal: {final_count}")
            #         print("Check end entries After",Claim_df['LossDate'])
            # except ValueError as e:
            #     print(f"There was an issue with the date format: {e}")


            #df_display = Claim_df
            original_count = len(merged_df)
            print(original_count)
            final_count = len(Claim_df)
            entries2 = original_count - final_count
            # print("Enrties removed due to Date conversion of edorsement ",entries2)
            print(f"Total entries: {original_count}")
            # print(f"Removed entries: {removed_count}")
            print(f"Total after removal: {final_count}")
            print("Check end entries After",Claim_df['LossDate'])


            
            Claim_df['Period'] = Claim_df['LossDate'].dt.year
            Claim_df['claim_count'] = 1
            #Claim_df['period'] = No_Claim_df['LossDate'].dt.year


            

            print("*****************************")
            print("DF_DISPLAYYYYYYYYYY",Claim_df.head())
            print("*****************************")



            print("check 4")
            # Store the DataFrame in the session for download


            print("NaN in UID:", Claim_df['UID'].isna().sum())
            print("NaN in Period:", Claim_df['Period'].isna().sum())
            Claim_df['UID'] = Claim_df['UID'].astype(str)
            Claim_df['Period'] = Claim_df['Period'].astype(str)

            check_df = Claim_df.groupby(['UID', 'Period']).agg({
                'claim_count': 'sum',
                'ClaimPaid': 'sum'
            }).reset_index()

            consol = check_df

            print("*********************************")
            print("CHECK DF IS ",check_df.head())
            print("*************************************")



            Claim_df.drop(['Period', 'claim_count'], axis=1, inplace=True)
            #No_Claim_df['LossDate'] = No_Claim_df['LossDate'].dt.strftime(translated_format)
            Claim_df['LossDate'] = Claim_df['LossDate'].dt.strftime(translated_format)
            df_display = Claim_df
            request.session['download_df'] = df_display.to_json(orient='split')




            new_df_json = request.session.get('new_df')
            #print(new_df_json)
            if new_df_json:
                new_df = pd.read_json(new_df_json, orient='split')
                new_df['UID'] = new_df['UID'].astype(str)
                new_df['Period'] = new_df['Period'].astype(str)
            else:
                # Handle the case where new_df is not in the session
                new_df = pd.DataFrame()  # or handle this scenario appropriately
            
            consol['UID'] = consol['UID'].astype(str)
            consol['Period'] = consol['Period'].astype(str)
            
            
            print("orphanorphan")
            if not new_df.empty:
                result_df = new_df.merge(consol, on=['UID', 'Period'], how='left') #new_df is premium and consol is claims
                print(consol)
                print(new_df)
                result_df['claim_count'] = result_df['claim_count'].fillna(0)
                orphan_mask = (result_df['claim_count'] == 0)
                print("orphan")
                print(orphan_mask)

                # Extract the UIDs and Periods of the orphan claims
                orphan_claims = result_df.loc[orphan_mask, ['UID', 'Period']]
                print("orphan")
                print(orphan_claims)
                # If you only need the IDs (UIDs) as a list, you can extract them like this:
                orphan_uids = orphan_claims['UID'].unique().tolist()
                orphan_uids=pd.DataFrame(orphan_uids, columns=['UID'])
                orphan_uids = result_df[orphan_mask]
                print("Orphan Claims")
                print(orphan_uids)
                




            else:
                result_df = consol  # or handle this scenario appropriately

            
            print("Orphan Claims")
            print(orphan_uids)
            orphan_uids = pd.DataFrame(orphan_uids, columns=['UIDs'])
                
            request.session['orphan_uids'] = orphan_uids.to_json(orient='split')
            orphan_uids_html = orphan_uids.head().to_html(classes='dataframe', index=False, escape=False)
            #request.session['download_df'] = Claim_df.to_json(orient='split')
            request.session['check_df'] = check_df.to_json(orient='split')
            request.session['result_df'] = result_df.to_json(orient='split')
            request.session['consol_df'] = result_df.to_json(orient='split')
            check_df = check_df.head().to_html(classes='dataframe', index=False, escape=False)
            
            result_df_formatted = result_df.head().copy()
            result_df_formatted['Exposure'] = result_df_formatted['Exposure'].round(3)
            result_df_formatted['UID_expsoure'] = result_df_formatted['UID_expsoure'].round(3)
            result_df_formatted['Gross Premium_SUM'] = result_df_formatted['Gross Premium_SUM'].round(0)
            #result_df_formatted['sum_Insured'] = result_df_formatted['sum_Insured'].round(0)
            result_df_formatted['EarnedPremium'] = result_df_formatted['EarnedPremium'].round(0)
            consol = result_df_formatted.head().to_html(classes='dataframe', index=False, escape=False)
            request.session['download_df'] = df_display.to_json(orient='split')
        else:
            
            one_to_one = pd.DataFrame()
            identifier_format = request.POST.get('identifier_format')
            print("*******************",identifier_format)
            print("2 merged", merged_df.head())
            received_format = request.POST.get('date_format')
            # translated_format = translate_format(received_format)
            # print("Translated format:", translated_format)
            # merged_df[loss_date_column] = merged_df[loss_date_column].apply(lambda x: try_parsing_date(x))
            print("3 merged", merged_df.head())

            # merged_df[payment_column] = pd.to_datetime(
            #     merged_df[payment_column],format=translated_format, errors='coerce'
            #          )
            print("4 merged", merged_df.head())
            print("*****************************")
            print("**********************")
            print('TOTAL DF',merged_df.head())
            print("UID COMING",uid_column)

            print("UID",merged_df['UID'].head())
            print("LossDate",merged_df[loss_date_column].head())
            print("ClaimType",merged_df[claim_type_column].head())
            
            claim_amount_column11 = request.POST.get('CLAIM_AMOUNT1')
            operator = request.POST.get('OPERATOR1')
            claim_amount_column22 = request.POST.get('CLAIM_AMOUNT2')
            print("CLaim amount 1",claim_amount_column11)
            print("CLaim amount 2",claim_amount_column22)
            print("OPT",operator)
            merged_df[claim_amount_column11] = pd.to_numeric(merged_df[claim_amount_column11], errors='coerce')
            merged_df[claim_amount_column22] = pd.to_numeric(merged_df[claim_amount_column22], errors='coerce')
            
            if (claim_amount_column11 is None) and (claim_amount_column22 is None):
                print("hello")
                claim_amount_column=claim_amount_column11
            elif (claim_amount_column22=='empty'):
                claim_amount_column=claim_amount_column11
            else:
                if operator=='+':
                    # Calculate the total claim paid
                    merged_df['Claim Paid'] = merged_df[claim_amount_column11] + merged_df[claim_amount_column22]
                    print("hello 11")
                    print(merged_df['Claim Paid'])
                    #merged_df['Claim Paid']= merged_df[claim_amount_column11]+merged_df[claim_amount_column22]
                elif operator=='-':
                    print("hello")
                    merged_df['Claim Paid']= merged_df[claim_amount_column11]-merged_df[claim_amount_column22] 
                claim_amount_column='Claim Paid'
            
            print(merged_df.columns)
            Claim_df = merged_df.groupby(['UID',claim_type_column,loss_date_column]).agg({
                claim_amount_column: 'sum',
            }).reset_index()

            null_lossDate_count = merged_df[loss_date_column].isnull().sum()
            null_lossDate = merged_df[loss_date_column].isnull()
            null_entries_df = merged_df[null_lossDate]
            null_lossDate_df = pd.DataFrame(null_entries_df)

            negative_claims_df = merged_df[merged_df[claim_amount_column] < 0]



            if identifier_format == 'ULC':
                No_Claim_df= merged_df.groupby(['UID', loss_date_column,claim_type_column])[claim_amount_column].sum().reset_index()
                No_Claim_df.columns = ['UID', 'LossDate','ClaimType', 'ClaimPaid']
            else:
                No_Claim_df= merged_df.groupby(['UID', loss_date_column])[claim_amount_column].sum().reset_index()
                No_Claim_df.columns = ['UID', 'LossDate', 'ClaimPaid']


            request.session['No_Claim_df'] = No_Claim_df.to_json(orient='split')
            
            print("This is not_claim_df",No_Claim_df.head())
            print("check4")

            
            
            claim_amounts_df = No_Claim_df.copy()

            # Convert the ClaimAmount_SUM column to numeric, setting errors to NaN
            claim_amounts_df['ClaimPaid'] = pd.to_numeric(claim_amounts_df['ClaimPaid'], errors='coerce')

            # Drop NaN values that resulted from the conversion
            claim_amounts_df.dropna(inplace=True)

            nan_count_before = claim_amounts_df['ClaimPaid'].isna().sum()

            # Drop NaN values that resulted from the conversion
            claim_amounts_df.dropna(subset=['ClaimPaid'], inplace=True)
            
            claim_entries1=nan_count_before

            total_after = claim_amounts_df.shape[0]

            # Filter the DataFrame to only contain negative values
            negative_claims_df = claim_amounts_df[claim_amounts_df['ClaimPaid'] < 0]

            # Count the number of negative ClaimAmount_SUM entries
            negative_claims_count = negative_claims_df['ClaimPaid'].count()

            print(f"The count of negative ClaimPaid entries is: {negative_claims_count}")
            No_Claim_df['LossDate'] = No_Claim_df['LossDate'].apply(lambda x: try_parsing_date11(x,translated_format))
            
            # try:
            #         original_count = len(merged_df)
            #         print(original_count)
            #         print(No_Claim_df.shape)
            #         No_Claim_df['LossDate'] = pd.to_datetime(
            #             No_Claim_df['LossDate'],
            #             format=translated_format, errors='coerce'
            #             #errors='coerce'  # This will replace non-parsable dates with NaT
            #         )
            #         # Drop rows where dates could not be parsed
            #         print("Check end entries before",No_Claim_df['LossDate'])
            #         #merged_df.dropna(subset=[loss_date_column], inplace=True)
            #         final_count = len(No_Claim_df)
            #         entries2 = original_count - final_count
            #         # print("Enrties removed due to Date conversion of edorsement ",entries2)
            #         print(f"Total entries: {original_count}")
            #         # print(f"Removed entries: {removed_count}")
            #         print(f"Total after removal: {final_count}")
            #         print("Check end entries After",No_Claim_df['LossDate'])
            # except ValueError as e:
            #     print(f"There was an issue with the date format: {e}")
            original_count = len(merged_df)
            print(original_count)
            final_count = len(No_Claim_df)
            entries2 = original_count - final_count
            # print("Enrties removed due to Date conversion of edorsement ",entries2)
            print(f"Total entries: {original_count}")
            # print(f"Removed entries: {removed_count}")
            print(f"Total after removal: {final_count}")
            print("Check end entries After",No_Claim_df['LossDate'])

            No_Claim_df['Period'] = No_Claim_df['LossDate'].dt.year
            No_Claim_df['claim_count'] = 1

            # No_Claim_df['period'] = No_Claim_df['LossDate'].dt.year
            # Assuming 'No_Claim_df' is your DataFrame

            print("No_Claim",No_Claim_df.head())
            
            
            # Store the DataFrame in the session for download


            # Group by 'UID' and 'Period', and then calculate the sum of 'claim_count' and 'ClaimAmount_SUM'
            grouped_df = No_Claim_df.groupby(['UID', 'Period']).agg({
                'claim_count': 'sum',
                'ClaimPaid': 'sum'
            }).reset_index()

            print("this is grouped_df",grouped_df.head())

            check_df = grouped_df
            consol = grouped_df
            No_Claim_df.drop(['Period', 'claim_count'], axis=1, inplace=True)
            No_Claim_df['LossDate'] = No_Claim_df['LossDate'].dt.strftime(translated_format)
            df_display = No_Claim_df

            # The grouped_df DataFrame now contains the sum of 'claim_count' and 'ClaimAmount_SUM' for each combination of 'UID' and 'Period'


            new_df_json = request.session.get('new_df')
            # print("new DF is 0",new_df.head())
            
            if new_df_json:
                new_df = pd.read_json(new_df_json, orient='split')
                consol['UID'] = consol['UID'].astype(str)
                consol['Period'] = consol['Period'].astype(str)
                new_df['UID'] = new_df['UID'].astype(str)
                new_df['Period'] = new_df['Period'].astype(str)
            else:
                # Handle the case where new_df is not in the session
                new_df = pd.DataFrame()  # or handle this scenario appropriately


            
            if not new_df.empty:
                result_df = new_df.merge(consol, on=['UID', 'Period'], how='left') #new_df is premium and consol is claims
                result_df[consol.columns] = result_df[consol.columns].fillna(0)
                # Identify orphan claims: rows where all columns from 'consol' are zeros
                # Create a boolean mask where all values in the 'consol' columns are 0
            else:
                result_df = pd.DataFrame()  # or handle this scenario appropriately
                print("result df s")

            

            # Replace 'Column1', 'Column2', etc. with actual column names from new_df
            # result_df = result_df.dropna(subset=['UID', 'Period'])
            # print("Successful matches:\n", result_df)



        # Store the DataFrame in the session for download
            request.session['check_df'] = check_df.to_json(orient='split')
            request.session['result_df'] = result_df.to_json(orient='split')
            request.session['NullLossDate'] = null_lossDate_df.to_json(orient='split')
            
            check_df = check_df.head().to_html(classes='dataframe', index=False, escape=False)
            result_df_formatted = result_df.head().copy()
            result_df_formatted['Exposure'] = result_df_formatted['Exposure'].round(3)
            result_df_formatted['UID_expsoure'] = result_df_formatted['UID_expsoure'].round(3)
            print(result_df_formatted)
            result_df_formatted['Gross Premium_SUM'] = result_df_formatted['Gross Premium_SUM'].round(0)
            #result_df_formatted['sum_Insured'] = result_df_formatted['sum_Insured'].round(0)
            result_df_formatted['EarnedPremium'] = result_df_formatted['EarnedPremium'].round(0)
            consol = result_df_formatted.head().to_html(classes='dataframe', index=False, escape=False)
            request.session['download_df'] = df_display.to_json(orient='split')
            #grouped_df_html = grouped_df.to_html(classes='dataframe', index=False, escape=False)



        result_df_html = result_df.to_html(classes='dataframe', index=False, escape=False)
        check_df1 = pd.read_json(request.session.get('check_df', '{}'), orient='split')
        result_df1 = pd.read_json(request.session.get('result_df', '{}'), orient='split')


        # results = {
        #     'df_html': df_display.head().to_html(classes='dataframe', index=False, escape=False),
        #     'grouped_df_html': check_df,
        #     'new_df_html': consol,
        #     'download_ready': True,
        #     'check_result':check_df1,
        #     'result_result':result_df1,
            
        # }

        NullLossDate_len = len(null_lossDate_df)
        negative_claim_entries_len = len(negative_claims_df)
        one_to_one_len = len(one_to_one)
        orphan_uids_len=len(orphan_uids)
        

        request.session['NullLossDate'] = null_lossDate_df.to_json(orient='split')
        request.session['negative_claim_entries'] = negative_claims_df.to_json(orient='split')
        request.session['one_to_one'] = one_to_one.to_json(orient='split')
        request.session['orphan_claims'] = orphan_uids.to_json(orient='split')
        
    



        results = {
        'df_html': df_display.head().to_html(classes='dataframe', index=False, escape=False),
        'grouped_df_html': check_df.to_html(classes='dataframe', index=False, escape=False) if isinstance(check_df, pd.DataFrame) else check_df,  # Assuming check_df is a DataFrame
        'new_df_html': consol.head().to_html(classes='dataframe', index=False, escape=False) if isinstance(consol, pd.DataFrame) else consol,# Assuming consol is a DataFrame
        'download_ready': True,
        # 'check_result': check_df1.to_dict('records') if isinstance(check_df1, pd.DataFrame) else check_df1,  # Convert DataFrame to list of dicts
        # 'result_result': result_df1.to_dict('records') if isinstance(result_df1, pd.DataFrame) else result_df1,  # Convert DataFrame to list of dicts
        'NullLossDate': null_lossDate_df.head().to_html(classes='dataframe', index=False, escape=False),
        'negative_claim_entries':negative_claims_df.head().to_html(classes='dataframe', index=False, escape=False),
        'one_to_one':one_to_one.head().to_html(classes='dataframe', index=False, escape=False),
        #'BlankPDate':null_payment.head().to_html(classes='dataframe', index=False, escape=False),
        'NaN_Claim':claim_entries1,
        'Total_Entries1':total_entries,
        'Total_after1':total_after,
        'NullLossDate_len':NullLossDate_len,
        'negative_claim_entries_len':negative_claim_entries_len,
        'one_to_one_len':one_to_one_len,
        'orphan_claims': orphan_uids.head().to_html(classes='dataframe', index=False, escape=False) if isinstance(orphan_uids, pd.DataFrame) else orphan_uids,
        'orphan_uids_len':orphan_uids_len,

    }
        serializable_results = convert_numpy(results)

        # Store the serializable results in the session
        store_results_in_session(request, 'claims_results', serializable_results)

        # Redirect to the display view
        
            # Redirect to the display view
        return redirect('display_claims_results')
        # Render the template with the context

        #return render(request, 'myapp/claimData.html', context)
    else:
        # Handle the case where method is not POST
        # For example, redirect to the home page or show an error message
        return HttpResponse("Invalid request.", status=400)
    



def display_claims_results(request):
    results = get_results_from_session(request, 'claims_results')
    if results is None:
        return HttpResponse("No results available. Please go through the processing step first.")
    return render(request, 'myapp/claimData.html', results)




def display_results(request):
    results = get_results_from_session(request, 'premium_results')
    if results is None:
        return HttpResponse("No results available. Please go through the processing step first.")
    
    return render(request, 'myapp/navbar.html', results)


import tempfile
import os

import sys
import pandas as pd
from django.shortcuts import render
# Assuming CSVFileUploadForm is defined elsewhere in your code

from django.shortcuts import render
from .forms import CSVFileUploadForm
import pandas as pd

import pyarrow.csv as pc
import pandas as pd
from django.shortcuts import render
from .forms import CSVFileUploadForm  # Ensure this is correctly imported from your forms module

def flush_session(request):
    request.session.flush()
    return JsonResponse({'message': 'Session has been flushed successfully!'})

def merge_and_display(request):
    #request.session.flush()  
    print("*****************Loading Data*******************")
    message = ""
    columns = []
    file_details = []  
    total_entries = 0 
    is_merged = False
    dataframes = []

    if request.method == 'POST':
        form = CSVFileUploadForm1(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('files')
            dataframes = []
            
            for file in files:
                df = pd.read_csv(file)
                num_entries = len(df)
                total_entries += num_entries  # Add to total entries
                file_details.append({'name': file.name, 'entries': num_entries})
                dataframes.append(df)

            merged_df = pd.concat(dataframes)
            # Convert the merged DataFrame to JSON and store it in the session
            request.session['merged_df'] = merged_df.to_json(orient='split')
            message = "Files Merged Successfully"
            is_merged = True
            # Store the column names in the session
            request.session['merged_columns'] = merged_df.columns.tolist()
            columns = merged_df.columns.tolist()

    else:
        form = CSVFileUploadForm1()

    return render(request, 'myapp/upload.html', {
        'form': form,
        'message': message,
        'is_merged': is_merged,
        'columns': columns,
        'file_details': file_details,  # Pass the file details to the template
        'total_entries': total_entries, # Pass the total entries to the template
    })



def fetch_unique_dates(request):
    # Attempt to load the DataFrame from the session
    merged_df = pd.read_json(request.session.get('merged_df', '{}'), orient='split')
    print(merged_df.head())
    
    # Get the column name from the request
    column = request.GET.get('column', '') #Column is name of cancellation column
    if column:
        try:
            # Ensure the column exists in the DataFrame to avoid KeyError
            if column in merged_df.columns:
                unique_values = sorted(merged_df[column].dropna().unique().tolist())
                return JsonResponse({'unique_values': unique_values})
            else:
                return JsonResponse({'error': f'Column {column} not found in DataFrame'}, status=404)
        except Exception as e:
            # Log the error or print to the console
            print(f"Error processing column {column}: {e}")
            return JsonResponse({'error': 'Internal Server Error'}, status=500)
    else:
        return JsonResponse({'error': 'No column specified'}, status=400)


def select_column_view(request):
    merged_df = pd.read_json(request.session.get('merged_df', '{}'), orient='split')
    totalEntries= len(merged_df)
    columns = merged_df.columns.tolist()
    return render(request, 'myapp/select_column.html', {'columns': columns})


def get_columns(request):
    # Load the DataFrame from the session
    merged_df = pd.read_json(request.session.get('merged_df', '{}'), orient='split')

    # Get the column names of the DataFrame
    columns = merged_df.columns.tolist()

    # Return the column names as a JSON response
    return JsonResponse({'columns': columns})



# def get_columns(request):
#     premium_csv = pd.read_csv(request.FILES.get('premium_file'))
#     excel_file = pd.ExcelFile(request.FILES.get('excel_file'))

#     print("Premium CSV Columns:", premium_csv.columns.tolist())  # This will show the column names
#     premium_columns = premium_csv.columns.tolist()

#     excel_columns = excel_file.sheet_names

#     return JsonResponse({'premium_columns': premium_columns, 'excel_columns': excel_columns})


def get_columns1(request):
    # Load the DataFrame from the session
    merged_df = pd.read_json(request.session.get('merged_df', '{}'), orient='split')

    # Assume 'premium_columns' and 'excel_columns' are predefined or calculated
    premium_columns = [col for col in merged_df.columns if "premium" in col]  # Example condition
    excel_columns = [col for col in merged_df.columns if col not in premium_columns]

    # Return the column names as a JSON response
    return JsonResponse({'premium_columns': premium_columns, 'excel_columns': excel_columns})


def get_unique_values(request):
    global column
    # Load the dataframe from the session
    merged_df = pd.read_json(request.session.get('merged_df', '{}'), orient='split')

    column = request.GET.get('column', '')
    unique_values = merged_df[column].unique().tolist()
    request.session['unique_values'] = unique_values
    print(request.POST) 
    print("Unique values:", unique_values)
    return JsonResponse({'unique_values': unique_values})



def get_unique_values1(request):
    column_name = request.GET.get('column')
    if not column_name:
        return JsonResponse({'error': 'Column name is required'}, status=400)

    # Assuming you have your DataFrame stored in the session or otherwise accessible
    df = pd.read_json(request.session.get('merged_df', '{}'), orient='split')
    if column_name not in df.columns:
        return JsonResponse({'error': 'Invalid column name'}, status=400)

    unique_values = df[column_name].value_counts().reset_index().values.tolist()
    data = [{'value': value[0], 'count': value[1]} for value in unique_values]

    return JsonResponse(data, safe=False)


def get_values(request):
    global column
    # Load the dataframe from the session
    merged_df = pd.read_json(request.session.get('merged_df', '{}'), orient='split')

    column = request.GET.get('column', '')
    values = merged_df[column].tolist()
    print(request.POST) 
    return JsonResponse({'values': values})


def translate_format11(input_format):
            format_translation = {
                'yyyy': '%Y',  # Replace 'yyyy' first to prevent conflict with 'yy'
                'mm': '%m',
                'dd': '%d',
                'yy': '%y'    # 'yy' should be replaced after 'yyyy' has been replaced
            }
            for key, value in format_translation.items():
                input_format = input_format.replace(key, value)
            return input_format

def try_parsing_date11(date_str, translated_format):
    """
    Attempts to parse the date string using the provided format.
    Returns the date if parsing is successful; otherwise, returns pd.NaT.
    """
    try:
        return pd.to_datetime(date_str, format=translated_format)
    except (ValueError, TypeError):
        return pd.NaT  # Return NaT if parsing fails

    

def process_data(request):
    received_format = request.POST.get('date_format')
    translated_format = translate_format11(received_format)

    
    print("entered in process")
    selected_values = request.session.get('selectedValues', [])
    print("Selected values are",selected_values)
    import pandas as pd 
    global entries1, entries2, entries3, entries4, entries5, entries6,filtered_df
    try:
        # Load the dataframe  from the session
        merged_df = pd.read_json(request.session.get('merged_df', '{}'), orient='split')

        if selected_values is not None and selected_values:
            uid_col = 'UID'
            merged_df['UID'] = merged_df[selected_values].astype(str).agg('-'.join, axis=1)
            print("Selected values",selected_values)
            print("column is",merged_df[uid_col])
            print("In condition")
        else:
            uid_col = request.POST.get('uid')
            print("UID COL IS",uid_col)

        date_format = request.POST.get('date_format')
        print("Format is",date_format)
        total_counts = len(merged_df)
        unique_values2 = request.session.get('unique_values', [])

        print("***********************************************************")

        print("Unique values are",unique_values2)
        start_dates = request.POST.getlist('start_date[]')
        end_dates = request.POST.getlist('end_date[]')

        #convert start and end date to date time
        # for column_name in start_dates:
        #     if column_name in merged_df.columns:
        #         merged_df[column_name] = merged_df[column_name].apply(lambda x: try_parsing_date(x))
        #         print(f"After conversion, dtype of {column_name}: {merged_df[column_name].dtype}")

        # print("END DATE COLUMNS BELOW")

        # # Process each column listed in end_dates
        # for column_name in end_dates:
        #     if column_name in merged_df.columns:
        #         merged_df[column_name] = merged_df[column_name].apply(lambda x: try_parsing_date(x))
        #         print(f"After conversion, dtype of {column_name}: {merged_df[column_name].dtype}")

        print("START-END DATE CONVERSION START")
        date_columns = start_dates + end_dates

        # Filter columns that exist in the DataFrame using intersection
        date_columns = list(set(date_columns).intersection(merged_df.columns))

        # Convert all date columns to datetime in a vectorized manner
        merged_df[date_columns] = merged_df[date_columns].apply(pd.to_datetime, errors='coerce')
        print("START-END DATE CONVERSION ENDS......")


        group_by_types = request.POST.getlist('group_by_type[]')
        # group_by_type_start_date= request.POST.getlist('group_by_type_start_date[]')
        # group_by_type_end_date= request.POST.getlist('group_by_type_end_date[]')
        print("Start Dates:", start_dates)
        print("End Dates:", end_dates)
        print("Group By Types:", group_by_types)
        print("Counts:", len(unique_values2), len(start_dates), len(end_dates), len(group_by_types))
        
        print("***************************************************************")
        print("UID COLUMN 1",uid_col)
        original_count = len(merged_df)
        null_uids_df = merged_df[merged_df[uid_col].isnull()]
        merged_df.dropna(subset=[uid_col], inplace=True)
        
        
        final_count = len(merged_df)
        entries1 = original_count - final_count
        print("UIDS Removed due to NUll are: ",entries1)


        endorsement_date_col = request.POST.get('endoresement_date')
        null_end_df = merged_df[merged_df[endorsement_date_col].isnull()]
        null_count_endor = merged_df[endorsement_date_col].isnull().sum()


        # Convert dates using the translated format, handling errors
        try:
            original_count = len(merged_df)
            print("Original count:", original_count)
            # merged_df[endorsement_date_col] = merged_df[endorsement_date_col].apply(lambda x: try_parsing_date(x))

            merged_df[endorsement_date_col] = merged_df[endorsement_date_col].apply(lambda x: try_parsing_date11(x, translated_format))


            # Optionally, you can still drop rows where dates could not be parsed and are NaT
            # If you prefer to keep these rows, you can comment out or remove the line below
            merged_df.dropna(subset=[endorsement_date_col], inplace=True)
            
            final_count = len(merged_df)
            print("Data after Conversion Endorsement Date")
            print(merged_df[endorsement_date_col])
            print(f"Total entries: {original_count}")
            print(f"Total after removal: {final_count}")
            print("Check end entries After",merged_df[endorsement_date_col])

        except Exception as e:  # Catching a more general exception
            print(f"There was an issue with the date parsing: {e}")



        endor_datatype = merged_df[endorsement_date_col].dtype
        print("type of edorsement column ",endor_datatype)

        # merged_df[endorsement_date_col] = merged_df[endorsement_date_col].dt.strftime(date_format)

        copy_dataframe = merged_df.copy()
        


        print("UID COLUMN 2",uid_col)
        
        copy_dataframe.sort_values(by=[uid_col, endorsement_date_col], ascending=[True, True], inplace=True)

        print("UID COLUMN 3",uid_col)

        endor_datatype = copy_dataframe[endorsement_date_col].dtype
        print(f"The datatype of the '{endorsement_date_col}' column is: {endor_datatype}")

        radio_choice = request.POST.get('radio_button_choice', 'Last')  # Default to 'Last' if no choice given

        selectedPreference = request.POST.get('selectedPreference')
        print("GOT THE SELECTED PREFERENCE",selectedPreference)

        # Handling duplicates in copy_dataframe
        if selectedPreference == "First":
            copy_dataframe = copy_dataframe.drop_duplicates(subset=uid_col, keep='first')
        else:  # If choice is 'Last' or any other unexpected value
            copy_dataframe = copy_dataframe.drop_duplicates(subset=uid_col, keep='last')

        # 6. Only include uid_col, endorsement_date_col, other columns selected using additional
        
        other_col = request.POST.getlist('other')
        custom_selected_values = request.session.get('customSelectedValues', [])
        print("***********************************")
        print(custom_selected_values)
        print("***********************************")
        columns_to_display = [uid_col, endorsement_date_col] + custom_selected_values
        print("***********************************")
        print(columns_to_display)
        print("***********************************")
        negative_exposures = request.session.get('negative_exposures', [])

        # uid_col = request.POST.getlist('uid')[0]  
        gross_premium_col = request.POST.getlist('gross_premium')[0]

        # uid_col = request.POST.get('uid')
        gross_premium_col = request.POST.get('gross_premium')
        print("actual column of gross",gross_premium_col)


        merged_df[gross_premium_col] = pd.to_numeric(merged_df[gross_premium_col], errors='coerce')
        merged_df[gross_premium_col] = merged_df[gross_premium_col].fillna(0)
        merged_df[gross_premium_col] = merged_df[gross_premium_col].astype(int)

        print("*****************Converted grois to numeric=  type*******************")

        # Create the UID_DATAFRAME
        UID_DATAFRAME = merged_df.groupby(uid_col)[gross_premium_col].sum().reset_index()
        print("Papu2")

        cancellation_col = request.POST.get('cancellation')
        
        other_col = request.POST.getlist('other')
        print("names of cols")
        print(merged_df.columns)

        
        print("*****************Converted All colums*******************")            
        start_date_preference = request.POST.get('start_date_preference','last')
        first_start_date = 'first_start_date'
        def apply_date_logic(dates, logic):
            """Applies a specified logic to a series of dates."""
            if logic == 'min':
                return dates.min()
            elif logic == 'max':
                return dates.max()
            elif logic == 'first':
                return dates.iloc[0] if not dates.empty else pd.NaT
            elif logic == 'last':
                return dates.iloc[-1] if not dates.empty else pd.NaT
            return pd.NaT

        def set_dates(row, group_by_type_start, group_by_type_end):
            """
            Assigns start_date and end_date for a policy based on the row's data.
            Uses vectorized operations to find a match and assigns normalized dates from the respective columns.
            Additionally, applies specific logic to the start and end dates.
            """
            column_select = request.POST.get('column_select')
            policy_type = row[column_select]  

            policy_type_map = dict(zip(unique_values2, zip(start_dates, end_dates)))

            start_col, end_col = policy_type_map.get(policy_type, (None, None))

            if start_col is not None and end_col is not None:
                start_date_series = pd.Series(row[start_col]) if start_col in row else pd.Series()
                end_date_series = pd.Series(row[end_col]) if end_col in row else pd.Series()

                start_date = apply_date_logic(start_date_series, group_by_type_start[unique_values2.index(policy_type)])
                end_date = apply_date_logic(end_date_series, group_by_type_end[unique_values2.index(policy_type)])
            else:
                start_date, end_date = pd.NaT, pd.NaT
            return pd.Series([start_date, end_date])


        print("Data in merged")
        print(merged_df.columns)

        print("UID COLUMN IS ",uid_col)
        
        # Sort based on UID and ENDORSEMENT_DATE
        merged_df.sort_values(by=[uid_col, endorsement_date_col], ascending=[True, True], inplace=True)
        
        try:
            print("Starting date processing")
            group_by_type_start = request.POST.getlist('group_by_type_start_date[]')
            group_by_type_end = request.POST.getlist('group_by_type_end_date[]')

            print("Group by start dates:", group_by_type_start)  # Debug print
            print("Group by end dates:", group_by_type_end)      # Debug print

            # Applying set_dates without dropping duplicates
            print("Applying date settings...")
            merged_df[['POLICY_START_DATE', 'POLICY_END_DATE']] = merged_df.apply(
                lambda row: set_dates(row, group_by_type_start, group_by_type_end), axis=1
            )
            print("Dates applied successfully.")

            # drop duplicates to keep only the last entry per UID if necessary
            print(f"Dropping duplicates based on {uid_col}...")
            updated_merged_df = merged_df.drop_duplicates(subset=uid_col, keep='last')
            
            print("Date processing completed successfully.")
            print("Resulting DataFrame head:", updated_merged_df.head())  # Show the first few rows of the updated DataFrame

        except Exception as e:
            print(f"Error during date processing: {e}")

         
        updated_merged_df = updated_merged_df[updated_merged_df[uid_col].notna()]

        # 7. Apply left join on copy_dataframe uid with updated_merged_df uid
        final_df = pd.merge(copy_dataframe, updated_merged_df[columns_to_display], on=uid_col, how='left')



        duplicated_entries = copy_dataframe[copy_dataframe.duplicated(subset=uid_col, keep=False)]

        
        show_sum_insured = request.POST.get('show_sum_insured')
        
        if show_sum_insured == 'Yes':
            SumInsured_DF = merged_df.copy()

            print(SumInsured_DF.shape)


            sum_insured_column = request.POST.get('column_name')
            print(f"Received sum_insured_column from POST request: {sum_insured_column}")

            sum_insured_choice = request.POST.get('sum_insured_choice', 'Total')
            print(f"Received sum_insured_choice from POST request: {sum_insured_choice}")

            if sum_insured_choice == "Incremental":
                SumInsured_DF[sum_insured_column] = pd.to_numeric(SumInsured_DF[sum_insured_column], errors='coerce')
                SumInsured_DF[sum_insured_column] = SumInsured_DF[sum_insured_column].fillna(0)
                SumInsured_DF[sum_insured_column] = SumInsured_DF[sum_insured_column].astype(int)

                SumInsured_DF_grouped = SumInsured_DF.groupby(uid_col)[sum_insured_column].sum().reset_index(name=f'{sum_insured_column}_SUM')
                sum_insured_sum_column = f"{sum_insured_column}_SUM"
                SumInsured_DF = SumInsured_DF_grouped  # Assigning grouped df back to SumInsured_DF for consistency
                print(SumInsured_DF.shape)

            else: 
                print(sum_insured_column)
                # Sort based on ENDORESEMENT_DATE in ascending order
                #endorsement_date_col = request.POST.get('endoresement_date')
                SumInsured_DF.sort_values(by=endorsement_date_col, ascending=True, inplace=True)
                
                # Get the date_preference from POST data ('first' or 'last')
                # Get the date_preference from POST data ('first' or 'last')
                date_preference = request.POST.get('sum_insured_timeframe')
                print("Value is ",date_preference)
                if date_preference not in ['First', 'Last']:
                    date_preference = 'last'  # Default to 'last' if the value is anything else or not provided
                # Drop duplicates but keep either the 'first' or 'last' based on date_preference
                keep = 'first' if date_preference == 'First' else 'last'
                SumInsured_DF = SumInsured_DF.drop_duplicates(subset=uid_col, keep=keep)[[uid_col, sum_insured_column]]

                # Renaming the column to reflect whether it's the 'FIRST' or 'LATEST' value
                sum_insured_sum_column = f"{sum_insured_column}_{'FIRST' if date_preference == 'First' else 'LATEST'}"
                SumInsured_DF.rename(columns={sum_insured_column: sum_insured_sum_column}, inplace=True)
                print(SumInsured_DF.shape)



            
            duplicated_entries = SumInsured_DF[SumInsured_DF.duplicated(subset=uid_col, keep=False)]

            if not duplicated_entries.empty:
                print(f"Duplicated entries found in copy_dataframe based on {uid_col}:")
                print(duplicated_entries)
                # If you're in a web context, you may replace the print statement with a logger or return a response
                return HttpResponse(f"Duplicated entries found in copy_dataframe based on {uid_col}.")


            final_df = pd.merge(final_df, SumInsured_DF, on=uid_col, how='left')
        
            

        if UID_DATAFRAME.shape[0] == final_df.shape[0]:

            # Print message to console
            print("Both UID_DATAFRAME and updated_merged_df have the same number of entries.")
            
            # Perform a left join to add GROSS_PREMIUM_LC column from UID_DATAFRAME to updated_merged_df
            updated_merged_df = pd.merge(updated_merged_df, UID_DATAFRAME, on=uid_col, how='left', suffixes=('', '_SUM'))

            
            print("CHECK 4")
            if (updated_merged_df['UID'] == 'P/300/2904/19/000025-3212').any():
                subset_df = updated_merged_df.loc[updated_merged_df['UID'] == 'P/300/2904/19/000025-3212', ['POLICY_START_DATE','POLICY_END_DATE']]
                print(subset_df)
            else:
                print("No rows with UID equal to 1 found.")


            print("****************************")
            print(updated_merged_df.head())
            print("***************************8")
            # final_df1 = pd.merge(final_df, updated_merged_df, on=uid_col, how='left')

            # Columns that you want from `updated_merged_df`. This is just an example; adjust it to your needs
            updated_merged_df_cols = list(updated_merged_df.columns.difference(final_df.columns))
            updated_merged_df_cols.append(uid_col)  # Make sure to include the uid column for merging

            final_df = pd.merge(final_df, updated_merged_df[updated_merged_df_cols], on=uid_col, how='left')
            original_count = len(final_df)

            print("final issssssssssss")
            print(final_df.head())



            #Data frames having null entries
            null_start_date_df = final_df[final_df['POLICY_START_DATE'].isnull()]
            null_end_date_df = final_df[final_df['POLICY_START_DATE'].isnull()]

            gross_null = final_df[final_df[gross_premium_col+'_SUM'].isnull()]
            negative_gross_df = final_df[final_df[gross_premium_col+'_SUM'] < 0]





            # Remove entries with a null 'POLICY_START_DATE' from the original DataFrame
            final_df = final_df[final_df['POLICY_START_DATE'].notnull()]
            final_count = len(final_df)
            entries_removed_due_to_null_start_date = original_count - final_count

            #for end
            final_df = final_df[final_df['POLICY_END_DATE'].notnull()]
            final_count = len(final_df)
            entries_removed_due_to_null_end_date = original_count - final_count
            
            # Calculate the number of days
            final_df['DURATION_DAYS'] = (final_df['POLICY_END_DATE'] - final_df['POLICY_START_DATE']).dt.days
            

            # Create separate DataFrames for the specified day ranges
            df_50_days = final_df[final_df['DURATION_DAYS'] <= 50].drop(columns=['DURATION_DAYS'])
            df_100_days = final_df[final_df['DURATION_DAYS'] <= 100].drop(columns=['DURATION_DAYS'])
            df_150_days = final_df[final_df['DURATION_DAYS'] <= 150].drop(columns=['DURATION_DAYS'])
            df_200_days = final_df[final_df['DURATION_DAYS'] <= 200].drop(columns=['DURATION_DAYS'])
            df_250_days = final_df[final_df['DURATION_DAYS'] <= 250].drop(columns=['DURATION_DAYS'])
            df_300_days = final_df[final_df['DURATION_DAYS'] <= 300].drop(columns=['DURATION_DAYS'])
            final_df=final_df.drop(columns=['DURATION_DAYS'])
            df_50_days_len=len(df_50_days)
            df_100_days_len=len(df_100_days)
            df_150_days_len = len(df_150_days)
            df_200_days_len = len(df_200_days)
            df_250_days_len = len(df_250_days)
            df_300_days_len = len(df_300_days)

            





            invalid_date_df = final_df[final_df['POLICY_START_DATE'] > final_df['POLICY_END_DATE']]
            final_df = final_df[final_df['POLICY_START_DATE'] <= final_df['POLICY_END_DATE']]
            final_count = len(final_df)
            entries6 = original_count - final_count
            print("Enrties removed due to Date less than PSD PED ",entries6)

            print("UIDS Removed due to NUll are: ",entries1)
            print("Enrties removed due to Date conversion of edorsement ",entries2)
            print("Enrties removed due to Date conversion of Start Date ",entries3)
            print("Enrties removed due to Date conversion of End Date ",entries4)
            print("Enrties removed due to Date conversion of Cancellation ",entries5)
            print("Enrties removed due to Date LESS THAN PSD PED ",entries6)


            print("finallll2",final_df.head())


            final_df['POLICY_END_DATE'] = pd.to_datetime(final_df['POLICY_END_DATE']).dt.normalize()
            final_df['POLICY_START_DATE'] = pd.to_datetime(final_df['POLICY_START_DATE']).dt.normalize()

            print("finallll3",final_df.head())

            print("START DATE TYPE",final_df['POLICY_START_DATE'].dtype)
            print("END DATE TYPE",final_df['POLICY_END_DATE'].dtype)
            
            print("finallll",final_df.head())

            value_of_exposure = request.POST.get("show_exposure")
            
            print(value_of_exposure)
            
            final_df['UID_expsoure'] = ((final_df['POLICY_END_DATE'] - final_df['POLICY_START_DATE']).dt.days + 1) / float(value_of_exposure) 
            
            
            

            exposure_df = final_df[(final_df['UID_expsoure'] < 0) | (final_df['UID_expsoure'] > 1.002054)]
            expsoure_df_size = len(exposure_df)
          
            show_sum_insured = request.POST.get('show_sum_insured')

            if show_sum_insured == 'Yes':
                PolicyFrame = [uid_col, 'POLICY_START_DATE', 'POLICY_END_DATE', gross_premium_col+'_SUM',sum_insured_sum_column,'UID_expsoure']+custom_selected_values
            else:
                PolicyFrame = [uid_col, 'POLICY_START_DATE', 'POLICY_END_DATE', gross_premium_col+'_SUM','UID_expsoure']+custom_selected_values

            PolicyD = final_df[PolicyFrame]


            def create_periods_df_yr(df):
                # Convert policy start and end dates to datetime format
                # df['POLICY_START_DATE'] = pd.to_datetime(df['POLICY_START_DATE'], format='%d-%m-%Y')
                # df['POLICY_END_DATE'] = pd.to_datetime(df['POLICY_END_DATE'], format='%d-%m-%Y')

                # Project start date and maximum PolicyEndDate
                project_start_date = df['POLICY_START_DATE'].min()
                max_policy_end_date = df['POLICY_END_DATE'].max()

                # Initialize variables for while loop
                periods_data = []
                current_start_date = project_start_date

                while current_start_date <= max_policy_end_date:
                    # Define period end date
                    if current_start_date.month == 1 and current_start_date.day == 1:
                        # Full year case: January 1st to December 31st
                        current_end_date = datetime(current_start_date.year, 12, 31)
                    else:
                        # First period: From start date to the end of the year
                        current_end_date = datetime(current_start_date.year, 12, 31)

                    # Ensure the end date does not exceed the policy end date
                    if current_end_date > max_policy_end_date:
                        current_end_date = max_policy_end_date

                    # Append the period data
                    periods_data.append([f"{current_start_date.year}", current_start_date, current_end_date])

                    # Move to the next period starting on January 1st of the following year
                    current_start_date = datetime(current_start_date.year + 1, 1, 1)

                # Creating the DataFrame
                periods_df = pd.DataFrame(periods_data, columns=["Period", "PeriodStartDate", "PeriodEndDate"])
                return periods_df
            


            # def create_periods_df_qtr(df):
            #     # Project start date and maximum PolicyEndDate
            #     project_start_date = datetime(df['POLICY_START_DATE'].min().year, 1, 1) 
            #     max_policy_end_date = df['POLICY_END_DATE'].max()

            #     # Initialize variables for while loop
            #     year = project_start_date.year
            #     quarter = 1
            #     periods_data = []
            #     while True:
            #         # Calculate the start date and end date for each quarter
            #         start_date = datetime(year, 3 * (quarter - 1) + 1, 1)
            #         end_date = (datetime(year, 3 * quarter + 1, 1) - pd.Timedelta(days=1)) if quarter < 4 else datetime(year, 12, 31)
                    
            #         # Check if the current period start date is after the maximum PolicyEndDate
            #         if start_date > max_policy_end_date:
            #             break
                    
            #         periods_data.append([f"Q{quarter} {year}", start_date, end_date])
                    
            #         # Update quarter and year
            #         if quarter == 4:
            #             quarter = 1
            #             year += 1
            #         else:
            #             quarter += 1

            #     # Creating the DataFrame
            #     periods_df = pd.DataFrame(periods_data, columns=["Period", "PeriodStartDate", "PeriodEndDate"])
            #     return periods_df

            def create_periods_df_qtr(df):
                # Project start date and maximum PolicyEndDate
                project_start_date = datetime(df['POLICY_START_DATE'].min().year, 1, 1) 
                max_policy_end_date = df['POLICY_END_DATE'].max()

                # Initialize variables for while loop
                year = project_start_date.year
                quarter = 1
                periods_data = []
                while True:
                    # Calculate the start date and end date for each quarter
                    start_date = datetime(year, 3 * (quarter - 1) + 1, 1)
                    end_date = (datetime(year, 3 * quarter + 1, 1) - pd.Timedelta(days=1)) if quarter < 4 else datetime(year, 12, 31)
                    
                    # Check if the current period start date is after the maximum PolicyEndDate
                    if start_date > max_policy_end_date:
                        break
                    
                    periods_data.append([f"Q{quarter} {year}", start_date, end_date, year])
                    
                    # Update quarter and year
                    if quarter == 4:
                        quarter = 1
                        year += 1
                    else:
                        quarter += 1

                # Creating the DataFrame
                periods_df = pd.DataFrame(periods_data, columns=["Period", "PeriodStartDate", "PeriodEndDate", "Period_Year"])
                #print("PERIOD DF FROM QUARTER IS", periods_df)
                return periods_df


            def process_data_split(df, periods_df):
                # Reset index and rename the 'index' column
                df.reset_index(inplace=True)

                # Initialize an empty DataFrame for the final result
                final_df = pd.DataFrame()

                # Iterate over each row in periods_df
                for i in range(len(periods_df)):
                    # Copy the original DataFrame
                    df_1 = df.copy()

                    # Assign period information to df_1
                    period = periods_df.iloc[i]
                    df_1['Period'] = period['Period']
                    df_1['PeriodStartDate'] = period['PeriodStartDate']
                    df_1['PeriodEndDate'] = period['PeriodEndDate']
                    
                    if 'Period_Year' in periods_df.columns:
                        df_1['Period_Year'] = period['Period_Year']

                    # Filter out rows based on policy start and end dates
                    df_1 = df_1[
                        ~((df_1['POLICY_START_DATE'] > df_1['PeriodEndDate']) | (df_1['POLICY_END_DATE'] < df_1['PeriodStartDate']))
                    ]

                    # Calculate effective start and end dates for each filtered entry
                    df_1['EffectiveStartDate'] = df_1[['POLICY_START_DATE', 'PeriodStartDate']].max(axis=1)
                    df_1['EffectiveEndDate'] = df_1[['POLICY_END_DATE', 'PeriodEndDate']].min(axis=1)

                    # Ensure the effective dates are of datetime type
                    df_1['EffectiveStartDate'] = pd.to_datetime(df_1['EffectiveStartDate'])
                    df_1['EffectiveEndDate'] = pd.to_datetime(df_1['EffectiveEndDate'])

                    # Append the filtered df_1 to final_df
                    final_df = pd.concat([final_df, df_1], ignore_index=True)

                # Calculate exposure
                final_df['Exposure'] = ((final_df['EffectiveEndDate'] - final_df['EffectiveStartDate'] + pd.Timedelta(days=1)).dt.days) / 365.25

                # Calculate earned premium
                final_df['EarnedPremium'] = (final_df['Exposure'] / final_df['UID_expsoure']) * final_df[gross_premium_col + '_SUM']

                # Sort final_df by 'index' and 'Period'
                final_df = final_df.sort_values(by=['index', 'Period'])

                # Drop unnecessary columns
                final_df_1 = final_df.drop(columns=['index', 'PeriodStartDate', 'PeriodEndDate'])

                return final_df_1

            selected_split = request.POST.get('split_type')
            if selected_split == 'Yearly':
                request.session['report_type'] = 'Yearly'
                selected_split = 'Year'
                print("Year is selected")
                year_split = create_periods_df_yr(PolicyD)
                new_df = process_data_split(PolicyD, year_split)
            elif selected_split == 'Quarterly':
                request.session['report_type'] = 'Quarterly'
                print("QUarter is selected ")
                selected_split = 'Quarter'
                Quarterly_split = create_periods_df_qtr(PolicyD)
                new_df = process_data_split(PolicyD, Quarterly_split)
                print('QUARTERLY DATA FRAME IS0',new_df.head())


            #Quarter_df = pd.DataFrame(new_df.head(10))
            print("Quarter split end")


            
            
            

            # Display the new DataFrame
            print("Desired")
            #print(new_df.head())


            
            print("******************************new")
            #print(new_df.head())
            new_df['POLICY_START_DATE'] = new_df['POLICY_START_DATE'].dt.strftime('%d-%m-%Y')
            new_df['POLICY_END_DATE'] = new_df['POLICY_END_DATE'].dt.strftime('%d-%m-%Y')
            new_df['EffectiveStartDate'] = new_df['EffectiveStartDate'].dt.strftime('%Y-%m-%d')
            new_df['EffectiveEndDate'] = new_df['EffectiveEndDate'].dt.strftime('%Y-%m-%d')


            less_than_one_df = new_df[new_df['UID_expsoure'] < 1]
            greater_than_one_df = new_df[new_df['UID_expsoure'] > 1]
            less_than_one_df_expo = new_df[new_df['Exposure'] < 1]
            greater_than_one_df_expo = new_df[new_df['Exposure'] > 1]
            request.session['new_df'] = new_df.to_json(orient='split')


            # Format the dates in the desired format including the time
            final_df['POLICY_END_DATE'] = final_df['POLICY_END_DATE'].dt.strftime('%Y-%m-%d %H:%M:%S')


            final_df[endorsement_date_col] = final_df[endorsement_date_col].dt.strftime(translated_format)
            print(final_df['POLICY_START_DATE'].iloc[0])
            final_df['POLICY_START_DATE'] = final_df['POLICY_START_DATE'].dt.strftime(translated_format)
            print(final_df['POLICY_START_DATE'].iloc[0])
            print(final_df['POLICY_END_DATE'].iloc[0])
            final_df['POLICY_END_DATE'] = pd.to_datetime(final_df['POLICY_END_DATE']).dt.strftime('%d-%m-%Y')
            print(final_df['POLICY_END_DATE'].iloc[0])
           

            




            TExposure = final_df['UID_expsoure']
            
            if show_sum_insured == 'Yes':
                columns_to_display = [uid_col, 'POLICY_START_DATE', 'POLICY_END_DATE', gross_premium_col+'_SUM',sum_insured_sum_column,'UID_expsoure']+custom_selected_values
            else:
                columns_to_display = [uid_col, 'POLICY_START_DATE', 'POLICY_END_DATE', gross_premium_col+'_SUM','UID_expsoure']+custom_selected_values
            filtered_df = final_df[columns_to_display]
            print("check filter",filtered_df.head())
            

            if show_sum_insured == 'Yes':
                filtered_df = filtered_df.rename(columns={
                uid_col: 'UID',
                sum_insured_sum_column: 'SumInsured',
                'POLICY_START_DATE': 'PolicyStartDate',
                'POLICY_END_DATE': 'PolicyEndDate',
                gross_premium_col+'_SUM': 'GrossPremium'
            }, inplace=False)
            else:
                filtered_df = filtered_df.rename(columns={
                uid_col: 'UID',
                'POLICY_START_DATE': 'PolicyStartDate',
                'POLICY_END_DATE': 'PolicyEndDate',
                gross_premium_col+'_SUM': 'GrossPremium'
            }, inplace=False)

            print("Filtered")
            print(filtered_df.head())
            
            uids = filtered_df['UID']
            if show_sum_insured == 'Yes':
                sum_insured = filtered_df['SumInsured']
            # else:
            #     sum_insured = filtered_df['GrossPremium']

            policy_start_dates = filtered_df['PolicyStartDate']
            policy_end_dates = filtered_df['PolicyEndDate']
            gross_premiums = filtered_df['GrossPremium']
            UID_expsoure = filtered_df['UID_expsoure']

            
            print(gross_premiums.head())
            if (len(gross_premiums.shape) == 2):
                gross_premiums = gross_premiums.iloc[0]
            print(gross_premiums.head())
            print("UID shape:", uids.shape)
            print("PolicyStartDate shape:", policy_start_dates.shape)
            print("PolicyEndDate shape:", policy_end_dates.shape)
            print("GrossPremium shape:", gross_premiums.shape)
            print("UID_exposure shape:", UID_expsoure.shape)
            

            if show_sum_insured == 'Yes':
                if (len(sum_insured.shape) == 2):
                    sum_insured = sum_insured.iloc[0]
                    print("SumInsured shape:", sum_insured.shape)

                PolicyDataframe = pd.DataFrame({
                'UID': uids,
                'SumInsured': sum_insured,
                'PolicyStartDate': policy_start_dates,
                'PolicyEndDate': policy_end_dates,
                'GrossPremium': gross_premiums,
                'UID_expsoure':UID_expsoure,
            })
            else:
                PolicyDataframe = pd.DataFrame({
                'UID': uids,
                'PolicyStartDate': policy_start_dates,
                'PolicyEndDate': policy_end_dates,
                'GrossPremium': gross_premiums,
                'UID_expsoure':UID_expsoure,
            })
                
            for column in custom_selected_values:
                if column not in PolicyDataframe:
                    PolicyDataframe[column] = column
            
            
                
            
            print(PolicyDataframe.head())
            print("AFter update")
        
            if show_sum_insured == 'Yes':
                filtered_df = filtered_df.rename(columns={
                sum_insured_column+'_SUM':'SumInsured',
            }, inplace=False)

            filtered_df = filtered_df.rename(columns={
                gross_premium_col+'_SUM': 'GrossPremium',
            }, inplace=False)
    
            # Save the updated dataframe back to the session
            request.session['final_df'] = filtered_df.to_json(orient='split')

            # print(endorsement_date_col, start_date_col)

            sum = entries1+entries2+entries3+entries4+entries5+entries6
            if entries1<=0:
                entries1=0
            elif entries2<=0:
                entries2=0
            elif entries3<=0:
                entries3=0
            elif entries4<=0:
                entries4=0
            elif entries5<=0:
                entries5=0
            elif entries6<=0:
                entries6=0
            elif entries_removed_due_to_null_start_date<=0:
                entries_removed_due_to_null_start_date=0
            elif entries_removed_due_to_null_end_date<=0:
                entries_removed_due_to_null_end_date=0


            print("negative gross",negative_gross_df.head())
            print("NULL",null_uids_df.head())
           
            print("Size is ",len(filtered_df))
            print("AT THE END DF")
            print(null_end_df.head())


            print("last",new_df.head())
            print(expsoure_df_size)
            
            
            NULL_ENDOR_UIDS_len = len(null_end_df)
            NULL_END_UIDS_len= len(null_end_date_df)
            NULL_EXPO_UIDS_len= len(exposure_df)
            NULL_INVALID_UIDS_len = len(invalid_date_df)
            NULL_NEGATIVE_UIDS_len = len(negative_gross_df)
            NULL_PREMIUM_UIDS_len = len(gross_null)
            NULL_START_UIDS_len = len(null_start_date_df)
            NULL_UIDS_UIDS_len = len(null_uids_df)
            less_than_one_df_len = len(less_than_one_df)
            greater_than_one_df_len = len(greater_than_one_df)
            less_than_one_df_expo_len = len(less_than_one_df_expo)
            greater_than_one_df_expo_len = len(greater_than_one_df_expo)
            request.session['NULL_START_UIDS'] = null_start_date_df.to_json(orient='split')
            request.session['NULL_END_UIDS'] = null_end_date_df.to_json(orient='split')
            request.session['Invalid_date'] = invalid_date_df.to_json(orient='split')
            request.session['gross_null'] = gross_null.to_json(orient='split')
            request.session['negative_gross_df'] = negative_gross_df.to_json(orient='split')
            request.session['null_uids_df'] = null_uids_df.to_json(orient='split')
            request.session['null_end_df'] = null_end_df.to_json(orient='split')
            request.session['exposure_df'] = exposure_df.to_json(orient='split')
            request.session['exposure_less_than_1'] = less_than_one_df.to_json(orient='split')
            request.session['exposure_more_than_1'] = greater_than_one_df.to_json(orient='split')
            request.session['exposure_less_than_1_expo'] = less_than_one_df_expo.to_json(orient='split')
            request.session['exposure_more_than_1_expo'] = greater_than_one_df_expo.to_json(orient='split')
            request.session['df_50_days'] = df_50_days.to_json(orient='split')
            request.session['df_100_days'] = df_100_days.to_json(orient='split')
            request.session['df_150_days'] = df_150_days.to_json(orient='split')
            request.session['df_200_days'] = df_200_days.to_json(orient='split')
            request.session['df_250_days'] = df_250_days.to_json(orient='split')
            request.session['df_300_days'] = df_300_days.to_json(orient='split')



            results={
                'dataframe': filtered_df.head().to_html(classes='dataframe', index=False, escape=False),
                'dataframe1': new_df.head().to_html(classes='dataframe', index=False, escape=False),
                'NULL_START_UIDS': null_start_date_df.to_html(classes='dataframe',index=False, escape=False),
                'NULL_END_UIDS': null_end_date_df.to_html(classes='dataframe',index=False, escape=False),
                'show_download_link': True,
                'original_count': total_counts,
                'removed_count': sum,
                'final_count': final_count,
                'UID_count': entries1,
                'END_DATE_count': entries2,
                'START_DATECOUNT':entries3,
                'END_DATE_COUNT':entries4,
                'CANCELLATION_DATE_COUNT':entries5,
                'GREATER_COUNT':entries6,
                'START_NULL_COUNT':entries_removed_due_to_null_start_date,
                'END_NULL_COUNT':entries_removed_due_to_null_end_date,
                'Invalid_date':invalid_date_df.head().to_html(classes='dataframe', index=False, escape=False),
                'gross_null':gross_null.head().to_html(classes='dataframe', index=False, escape=False),
                'negative_gross_df':negative_gross_df.head().to_html(classes='dataframe', index=False, escape=False),
                'null_uids_df':null_uids_df.head().to_html(classes='dataframe', index=False, escape=False),
                'null_end_df':null_end_df.head().to_html(classes='dataframe', index=False, escape=False),
                'Null_endorsement_count':null_count_endor,
                'exposure_df':exposure_df.head().to_html(classes='dataframe', index=False, escape=False),
                'NULL_ENDOR_UIDS_len': NULL_ENDOR_UIDS_len,
                'NULL_END_UIDS_len': NULL_END_UIDS_len,
                'NULL_EXPO_UIDS_len': NULL_EXPO_UIDS_len,
                'NULL_INVALID_UIDS_len': NULL_INVALID_UIDS_len,
                'NULL_NEGATIVE_UIDS_len': NULL_NEGATIVE_UIDS_len,
                'NULL_PREMIUM_UIDS_len': NULL_PREMIUM_UIDS_len,
                'NULL_START_UIDS_len': NULL_START_UIDS_len,
                'NULL_UIDS_UIDS_len': NULL_UIDS_UIDS_len,
                'exposure_less_than_1': less_than_one_df.head().to_html(classes='dataframe', index=False, escape=False),
                'exposure_more_than_1': greater_than_one_df.head().to_html(classes='dataframe', index=False, escape=False),
                'exposure_less_than_1_len':less_than_one_df_len,
                'exposure_more_than_1_len':greater_than_one_df_len,
                'exposure_less_than_1_expo': less_than_one_df_expo.head().to_html(classes='dataframe', index=False, escape=False),
                'exposure_more_than_1_expo': greater_than_one_df_expo.head().to_html(classes='dataframe', index=False, escape=False),
                'exposure_less_than_1_len_expo':less_than_one_df_expo_len,
                'exposure_more_than_1_len_expo':greater_than_one_df_expo_len,
                'df_50_days': df_50_days.head().to_html(classes='dataframe', index=False, escape=False),
                'df_100_days': df_100_days.head().to_html(classes='dataframe', index=False, escape=False),
                'df_150_days': df_150_days.head().to_html(classes='dataframe', index=False, escape=False),
                'df_200_days': df_200_days.head().to_html(classes='dataframe', index=False, escape=False),
                'df_250_days': df_250_days.head().to_html(classes='dataframe', index=False, escape=False),
                'df_300_days': df_300_days.head().to_html(classes='dataframe', index=False, escape=False),
                'df_50_days_len': df_50_days_len,
                'df_100_days_len': df_100_days_len,
                'df_150_days_len': df_150_days_len,
                'df_200_days_len': df_200_days_len,
                'df_250_days_len': df_250_days_len,
                'df_300_days_len': df_300_days_len,
                #'Quarter_split':  Quarter_df.head().to_html(classes='dataframe', index=False, escape=False),
            }
            serializable_results = convert_numpy(results)

        # Store the serializable results in the session
            serializable_results = convert_numpy(results)

        # Store the serializable results in the session
            store_results_in_session(request, 'premium_results', serializable_results)
        
            # Redirect to the display view
            return redirect('display_results')
        else:
            # Find out which UIDs are causing the discrepancy
            diff_uids = set(UID_DATAFRAME[uid_col]) - set(updated_merged_df[uid_col])
            print(f"UIDs present in UID_DATAFRAME but not in updated_merged_df: {diff_uids}")

            diff_uids = set(updated_merged_df[uid_col]) - set(UID_DATAFRAME[uid_col])
            print(f"UIDs present in updated_merged_df but not in UID_DATAFRAME: {diff_uids}")
            
            # Return a message if the entries are not the same
            return HttpResponse("Dataframes don't have the same number of entries.")

    except KeyError as e:
        print(e)
        return HttpResponse(f"Error: Column {e} not found in merged dataframe.")

def combined_results(request):
    result1 = get_results_from_session(request, 'os_results')
    result2 = get_results_from_session(request, 'claims_results')
    result3 = get_results_from_session(request, 'premium_results')
    combined = {
        'os_results':result1,
        'claims_results':result2,
        'premium_results':result3,
    }
    if result3 and 'dataframe' in result3:
        if result3['dataframe']:
            print("Premium Results df_html contains data.")
        else:
            print("Premium Results df_html is empty.")
    else:
        print("Premium Results does not exist or df_html attribute is not present.")
    return render(request, 'myapp/combined_results.html', combined)




import numpy as np




@csrf_exempt
def save_negative_exposures(request):
    if request.method == "POST":
        data = json.loads(request.body)
        request.session['negative_exposures'] = data.get('negative_exposures', [])
    return JsonResponse({'status': 'success'})


def handle_selected_values(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        request.session['selectedValues'] = data.get('selectedValues', [])
        print("Selected Vluare are",request.session['selectedValues'])
        # Process the selected_values as needed...
        return JsonResponse({'status': 'success', 'message': 'Selected values received'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def handle_custom_selected_values(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            custom_selected_values = data.get('customSelectedValues', [])
            request.session['customSelectedValues'] = custom_selected_values
            return JsonResponse({'status': 'success', 'message': 'Custom selected values received and processed'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

def checks_left_view(request):
    context = {
        'dataframe': filtered_df.head().to_html(classes='dataframe', index=False, escape=False),
        }
    return render(request, 'myapp/checksLeft.html', context)


def download_csv(request):
    # Load the updated dataframe from the session
    updated_merged_df = pd.read_json(request.session.get('final_df', '{}'), orient='split')
    #updated_merged_df = pd.read_json(request.session.get('updated_merged_df', '{}'), orient='split')
    
    # Convert the dataframe to CSV
    csv_data = updated_merged_df.to_csv(index=False)
    
    # Create a response with the CSV data
    response = HttpResponse(csv_data, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="updated_merged_data.csv"'
    
    return response

def download_csv1(request):
    # Load the updated dataframe from the session
    updated_merged_df = pd.read_json(request.session.get('final_df', '{}'), orient='split')
    #updated_merged_df = pd.read_json(request.session.get('updated_merged_df', '{}'), orient='split')
    #updated_merged_df_copy = updated_merged_df.copy()
    updated_merged_df = updated_merged_df.rename(columns={
    'PolicyStartDate': 'Policy_Start_Date',
    'PolicyEndDate': 'Policy_End_Date'})
    
    # Convert the dataframe to CSV
    csv_data = updated_merged_df.to_csv(index=False)
    
    # Create a response with the CSV data
    response = HttpResponse(csv_data, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="updated_merged_data.csv"'
    
    return response



def claims(request):
    try:
        template = loader.get_template('myapp/claims.html')
    except Exception as e:
        return HttpResponse(f"Error loading template: {e}", status=500)
    return HttpResponse(template.render({}, request))



# def download_reported_claims(request):
#     # Retrieve the DataFrame to download from the session
#     df_json = request.session.get('download_reported')
#     if df_json:
#         print(df_json)  # Debug: See the JSON string
#         try:
#             df = pd.read_json(df_json, orient='split')
#         except ValueError as e:
#             # Handle the error if the JSON structure is unexpected
#             print(e)
#             return HttpResponse("Error processing data to download.", status=500)

#         response = HttpResponse(content_type='text/csv')
#         response['Content-Disposition'] = 'attachment; filename="Reported_Claims.csv"'
#         df.to_csv(path_or_buf=response, index=False)
#         return response
#     else:
#         return HttpResponse("No data to download.", status=400)

    
def download_reported_claims(request):
    # Retrieve the DataFrame to download from the session
    df_json = request.session.get('check_df')
    if df_json:
        df = pd.read_json(df_json, orient='split')
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Reported_Claims.csv"'
        df.to_csv(path_or_buf=response, index=False)
        return response
    else:
        return HttpResponse("No data to download.", status=400)
    
def download_reported_claims_UAE(request):
    # Retrieve the DataFrame to download from the session
    df_json = request.session.get('check_df')
    if df_json:
        df = pd.read_json(df_json, orient='split')
        df = df.rename(columns={
        'ClaimType': 'Claim_Type',
        'OsPaid': 'GrossClaimsOutstanding'})
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Reported_Claims.csv"'
        df.to_csv(path_or_buf=response, index=False)
        return response
    else:
        return HttpResponse("No data to download.", status=400)

def download_processed_data(request):
    # Retrieve the DataFrame to download from the session
    df_json = request.session.get('download_df')
    if df_json:
        df = pd.read_json(df_json, orient='split')
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="processed_data.csv"'
        df.to_csv(path_or_buf=response, index=False)
        return response
    else:
        return HttpResponse("No data to download.", status=400)
    

def download_processed_data_UAE(request):
    # Retrieve the DataFrame to download from the session
    df_json = request.session.get('download_df')
    if df_json:
        df = pd.read_json(df_json, orient='split')
        df = df.rename(columns={
        'ClaimType': 'Claim_Type',
        'ClaimPaid': 'GrossClaimsPaid'})
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="processed_data.csv"'
        df.to_csv(path_or_buf=response, index=False)
        return response
    else:
        return HttpResponse("No data to download.", status=400)
    
    
def download_processed_data_os_UAE(request):
    # Retrieve the DataFrame to download from the session
    df_json = request.session.get('download_df')
    if df_json:
        df = pd.read_json(df_json, orient='split')
        df = df.rename(columns={
        'ClaimType': 'Claim_Type',
        'OsPaid': 'GrossClaimsOutstanding'})
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="processed_data.csv"'
        df.to_csv(path_or_buf=response, index=False)
        return response
    else:
        return HttpResponse("No data to download.", status=400)
    

def download_new_df_csv(request):
    # Load new_df from the session
    new_df = pd.read_json(request.session.get('new_df', '{}'), orient='split')
    # Convert the dataframe to CSV
    csv_data = new_df.to_csv(index=False)
    
    # Create a response with the CSV data
    response = HttpResponse(csv_data, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="new_data.csv"'
    
    return response

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

from django.shortcuts import render

def premium_checks(request):
    return render(request, 'myapp/PremiumChecks.html')


def quarter_data(request):
    # Load result_df from the session
    result_df = pd.read_json(request.session.get('Quarter_df', '{}'), orient='split')
    
    # Convert the dataframe to CSV
    csv_data = result_df.to_csv(index=False)
    
    # Create a response with the CSV data
    response = HttpResponse(csv_data, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Quarter_data.csv"'
    
    return response

def download_result_df_csv(request):
    # Load result_df from the session
    result_df = pd.read_json(request.session.get('result_df', '{}'), orient='split')
    
    # Convert the dataframe to CSV
    csv_data = result_df.to_csv(index=False)
    
    # Create a response with the CSV data
    response = HttpResponse(csv_data, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="result_data.csv"'
    
    return response


def download_checks(request):
    # Extract the name of the DataFrame from the request
    dataframe_name = request.GET.get('name')  # Assuming passed as a GET parameter
    
    # Retrieve the DataFrame JSON string from the session
    df_json = request.session.get(dataframe_name, None)
    
    if not df_json:
        return HttpResponse("Requested data not found in session", status=404)
    
    # Convert JSON string back to DataFrame
    df = pd.read_json(df_json, orient='split')
    
    # Convert the DataFrame to CSV
    csv_data = df.to_csv(index=False)
    
    # Create a response with the CSV data
    response = HttpResponse(csv_data, content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{dataframe_name}.csv"'
    
    return response



# def upload_mapping(request):
#     #request.session.flush()
#     print("*****************Loading Data*******************")
#     message = ""
#     columns = []
#     file_details = []  
#     total_entries = 0 
#     is_merged = False
#     dataframes = []

#     if request.method == 'POST':
#         form = CSVFileUploadForm1(request.POST, request.FILES)
#         if form.is_valid():
#             files = request.FILES.getlist('files')
#             dataframes = []
            
#             for file in files:
#                 df = pd.read_csv(file)
#                 num_entries = len(df)
#                 total_entries += num_entries  # Add to total entries
#                 file_details.append({'name': file.name, 'entries': num_entries})
#                 dataframes.append(df)

#             merged_df = pd.concat(dataframes)
#             # Convert the merged DataFrame to JSON and store it in the session
#             request.session['merged_df'] = merged_df.to_json(orient='split')
#             message = "Files Merged Successfully"
#             is_merged = True
#             # Store the column names in the session
#             request.session['merged_columns'] = merged_df.columns.tolist()
#             columns = merged_df.columns.tolist()

#     else:
#         form = CSVFileUploadForm1()

#     return render(request, 'myapp/Mapping_upload.html', {
#         'form': form,
#         'message': message,
#         'is_merged': is_merged,
#         'columns': columns,
#         'file_details': file_details,  # Pass the file details to the template
#         'total_entries': total_entries, # Pass the total entries to the template
#     })



from io import BytesIO
from django.http import HttpResponse


# Mapping as header

# def download_excel(request):
#     import json
#     import pandas as pd
#     from io import BytesIO
#     from django.http import HttpResponse

#     # Parse JSON data from the request body
#     data = json.loads(request.body)
#     selected_columns = data.get('selected_columns', [])

#     # Log the selected columns to verify
#     print("Selected Columns:", selected_columns)

#     # Load DataFrame from session (make sure it's properly stored as JSON)
#     merged_df = pd.read_json(request.session.get('merged_df', '{}'), orient='split')
#     print("DataFrame Head:", merged_df.head())

#     # Create filtered data for selected columns
#     filtered_data = {column: merged_df[[column]].dropna() for column in selected_columns if column in merged_df.columns}
#     print("Filtered Data Keys:", filtered_data.keys())

#     # Create an Excel file in-memory
#     output = BytesIO()
#     with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
#         for column, data in filtered_data.items():
#             if not data.empty:
#                 # Create value counts with dynamic column names
#                 value_counts = data[column].value_counts().reset_index()
#                 value_counts.columns = [column, 'Count']  # Use the column name dynamically

#                 # Add a new empty "Mapping" column
#                 value_counts['Mapping'] = pd.Series([''] * len(value_counts))

#                 value_counts.to_excel(writer, sheet_name=column, index=False)
    
#     # Reset the position to the beginning of the stream
#     output.seek(0)

#     # Create a response
#     response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#     response['Content-Disposition'] = 'attachment; filename="selected_data.xlsx"'
#     return response


from django.shortcuts import render
import pandas as pd

def upload_mapping(request):
    print("*****************Loading Data*******************")
    message = ""
    columns = []
    file_details = []  
    total_entries = 0 
    is_merged = False
    dataframes = []

    # Check if data is available in session
    merged_df_json = request.session.get('new_df')
    if merged_df_json:
        merged_df = pd.read_json(merged_df_json, orient='split')
        total_entries = merged_df.shape[0]  # Get the total number of entries
        columns = merged_df.columns.tolist()  # Get the list of columns
        message = "Data retrieved from session."
        is_merged = True
    else:
        message = "No data found in session. Please upload data."

    return render(request, 'myapp/Mapping_upload.html', {
        'message': message,
        'is_merged': is_merged,
        'columns': columns,
        'total_entries': total_entries,  # Pass the total entries to the template
    })

# def Naming_Convention(request):
#     print("*****************Loading Data*******************")
#     message = ""
#     columns = []
#     file_details = []  
#     total_entries = 0 
#     is_merged = False
#     dataframes = []

#     # Check if data is available in session
#     merged_df_json = request.session.get('result_df1')
#     if merged_df_json:
#         merged_df = pd.read_json(merged_df_json, orient='split')
#         total_entries = merged_df.shape[0]  # Get the total number of entries
#         columns = merged_df.columns.tolist()  # Get the list of columns
#         message = "Data retrieved from session."
#         is_merged = True
#     else:
#         message = "No data found in session. Please upload data."

#     return render(request, 'myapp/UAE_Naming.html', {
#         'message': message,
#         'is_merged': is_merged,
#         'columns': columns,
#         'total_entries': total_entries,  # Pass the total entries to the template
#     })

def Naming_Convention(request):
    print("*****************Loading Data*******************")
    message = ""
    columns = []
    file_details = []  
    total_entries = 0 
    is_merged = False
    dataframes = []

    # Check if data is available in session
    merged_df_json = request.session.get('result_df1')
    if merged_df_json:
        merged_df = pd.read_json(merged_df_json, orient='split')
        total_entries = merged_df.shape[0]  # Get the total number of entries
        columns = merged_df.columns.tolist()  # Get the list of columns
        message = "Data retrieved from session."
        is_merged = True
        
        # Split the columns into two lists for the left and right tables
        half = len(columns) // 2
        left_columns = columns[:half]
        right_columns = columns[half:]
    else:
        message = "No data found in session. Please upload data."
        left_columns = []
        right_columns = []

    return render(request, 'myapp/UAE_Naming.html', {
        'message': message,
        'is_merged': is_merged,
        'left_columns': left_columns,
        'right_columns': right_columns,
        'total_entries': total_entries,  # Pass the total entries to the template
    })

from io import StringIO

def update_and_download(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        selected_columns = data.get('selected_columns', [])
        new_column_names = data.get('new_column_names', [])

        if not selected_columns or not new_column_names:
            return JsonResponse({'error': 'Invalid data'}, status=400)

        # Retrieve the dataframe from the session
        merged_df_json = request.session.get('result_df1')
        if not merged_df_json:
            return JsonResponse({'error': 'No data available in session'}, status=400)

        merged_df = pd.read_json(merged_df_json, orient='split')

        # Update the column names
        column_mapping = dict(zip(selected_columns, new_column_names))
        merged_df.rename(columns=column_mapping, inplace=True)

        # Convert the updated dataframe to CSV
        csv_buffer = StringIO()
        merged_df.to_csv(csv_buffer, index=False)

        # Prepare the response for download
        response = HttpResponse(csv_buffer.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=updated_data.csv'
        return response

    return JsonResponse({'error': 'Invalid request method'}, status=405)



def download_excel(request):
    import json
    import pandas as pd
    from io import BytesIO
    from django.http import HttpResponse

    # Parse JSON data from the request body
    data = json.loads(request.body)
    selected_columns = data.get('selected_columns', [])

    # Log the selected columns to verify
    print("Selected Columns:", selected_columns)

    # Load DataFrame from session (make sure it's properly stored as JSON)
    merged_df = pd.read_json(request.session.get('new_df', '{}'), orient='split')
    print("DataFrame Head:", merged_df.head())

    # Create filtered data for selected columns
    filtered_data = {column: merged_df[[column]].dropna() for column in selected_columns if column in merged_df.columns}
    print("Filtered Data Keys:", filtered_data.keys())

    # Create an Excel file in-memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for column, data in filtered_data.items():
            if not data.empty:
                # Create value counts with dynamic column names
                value_counts = data[column].value_counts().reset_index()
                value_counts.columns = [column, 'Count']  # Use the column name dynamically

                # Add a new "Mapping{sheetName}" column dynamically named based on the sheet name
                mapping_column_name = f'Mapping_{column}'
                value_counts[mapping_column_name] = pd.Series([''] * len(value_counts))

                value_counts.to_excel(writer, sheet_name=column, index=False)

    # Reset the position to the beginning of the stream
    output.seek(0)

    # Create a response
    response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="selected_data.xlsx"'
    return response



from .forms import ExcelUploadForm, CSVFileUploadForm
import pandas as pd

# def MappingData(request):
#     excel_form = ExcelUploadForm(request.POST or None, request.FILES or None)
#     csv_form = CSVFileUploadForm(request.POST or None, request.FILES or None)
#     message = ''

#     if request.method == 'POST':
#         if excel_form.is_valid() and 'excel_file' in request.FILES:
#             excel_file = excel_form.cleaned_data['excel_file']
#             excel_path = handle_uploaded_file(excel_file, 'excel')
#             # Here you could process the excel file directly or return the path to the user for confirmation
#             message = 'Excel file uploaded successfully! '

#         if csv_form.is_valid() and 'premium_file' in request.FILES:
#             csv_file = csv_form.cleaned_data['premium_file']
#             csv_path = handle_uploaded_file(csv_file, 'csv')
#             # Similarly, handle the CSV file directly here
#             message += 'CSV file uploaded successfully! '

#     context = {
#         'excel_form': excel_form,
#         'csv_form': csv_form,
#         'message': message
#     }
#     return render(request, 'myapp/MappingData.html', context)

def MappingData(request):
    excel_form = ExcelUploadForm(request.POST or None, request.FILES or None)
    message = ''

    if request.method == 'POST':
        if excel_form.is_valid() and 'excel_file' in request.FILES:
            excel_file = excel_form.cleaned_data['excel_file']
            excel_path = handle_uploaded_file(excel_file, 'excel')
            message = 'Excel file uploaded successfully!'

    context = {
        'excel_form': excel_form,
        'message': message
    }
    return render(request, 'myapp/MappingData.html', context)


import os

def fetch_column_data(request):
    excel_file = request.FILES.get('excel_file')
    if excel_file is None:
        return JsonResponse({'error': 'Excel file not provided'}, status=400)

    # Read premium data from session
    new_df_json = request.session.get('new_df')
    if new_df_json:
        premium_df = pd.read_json(new_df_json, orient='split')
        premium_columns = premium_df.columns.tolist()
    else:
        return JsonResponse({'error': 'Session does not contain premium data'}, status=500)

    try:
        excel = pd.ExcelFile(excel_file)
        excel_columns = excel.sheet_names
    except Exception as e:
        return JsonResponse({'error': f'Failed to read Excel file: {str(e)}'}, status=500)

    return JsonResponse({'premium_columns': premium_columns, 'excel_columns': excel_columns})


def handle_uploaded_file(file, file_type):
    # Define file path based on file type
    file_path = f'media/{file_type}_{file.name}'
    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    return file_path





# def get_columns(request):
#     excel_columns = request.session.get('excel_columns', [])
#     premium_columns = request.session.get('premium_columns', [])
#     return JsonResponse({
#         'excel_columns': excel_columns,
#         'premium_columns': premium_columns
#     })

# def process_mapping_data(request):
#     if request.method == 'POST':
#         try:
#             excel_file = request.FILES.get('excel_file')
#             csv_file = request.FILES.get('premium_file')

#             if not excel_file or not csv_file:
#                 return JsonResponse({'error': 'Excel or CSV file not found in request'}, status=400)

#             mappings_data = request.POST.get('mappings')
#             if not mappings_data:
#                 return JsonResponse({'error': 'Mappings data not provided'}, status=400)

#             mappings = json.loads(mappings_data)
#             premium_df = pd.read_csv(csv_file)
#             excel = pd.ExcelFile(excel_file)
#             results = []

#             # Process all mappings and combine them into a single DataFrame for download
#             for mapping in mappings:
#                 sheet_df = pd.read_excel(excel, sheet_name=mapping['sheetName'])
#                 if 'Count' in sheet_df.columns:
#                     sheet_df.drop('Count', axis=1, inplace=True)

#                 result_df = pd.merge(
#                     sheet_df, premium_df, left_on=sheet_df.columns[0], right_on=mapping['columnName'], how='left'
#                 )
#                 results.append(result_df)

#             # Combine all results into one DataFrame if there are multiple mappings
#             if results:
#                 combined_df = pd.concat(results)

#                 # Convert DataFrame to CSV
#                 response = HttpResponse(content_type='text/csv')
#                 response['Content-Disposition'] = 'attachment; filename="updated_premium_file.csv"'

#                 combined_df.to_csv(path_or_buf=response, index=False)
#                 return response
#             else:
#                 return JsonResponse({'error': 'No data processed'}, status=400)

#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)
#     else:
#         return JsonResponse({'error': 'Invalid HTTP method'}, status=405)


# def process_mapping_data(request):
#     import json
#     import pandas as pd
#     from django.http import JsonResponse, HttpResponse

#     if request.method == 'POST':
#         try:
#             excel_file = request.FILES.get('excel_file')
#             csv_file = request.FILES.get('premium_file')

#             if not excel_file or not csv_file:
#                 return JsonResponse({'error': 'Excel or CSV file not found in request'}, status=400)

#             mappings_data = request.POST.get('mappings')
#             if not mappings_data:
#                 return JsonResponse({'error': 'Mappings data not provided'}, status=400)

#             mappings = json.loads(mappings_data)
#             premium_df = pd.read_csv(csv_file)
#             excel = pd.ExcelFile(excel_file)
#             results = []

#             # Process all mappings and combine them into a single DataFrame for download
#             for mapping in mappings:
#                 sheet_name = mapping['sheetName']
#                 sheet_df = pd.read_excel(excel, sheet_name=sheet_name)
#                 mapping_column_name = f'Mapping_{sheet_name}'  # dynamically construct the mapping column name

#                 # Ensure only necessary columns are processed
#                 if mapping_column_name in sheet_df.columns:
#                     sheet_df = sheet_df[[sheet_name, mapping_column_name]]
#                     # Perform the left join using the specified mapping
#                     result_df = pd.merge(
#                         premium_df, sheet_df, left_on=mapping['columnName'], right_on=sheet_name, how='left'
#                     )
#                     # Include this merged data in results
#                     results.append(result_df)
#                 else:
#                     # Log or handle the case where the expected mapping column does not exist
#                     print(f"Expected mapping column '{mapping_column_name}' not found in sheet '{sheet_name}'.")

#             # Combine all results into one DataFrame if there are multiple mappings
#             if results:
#                 combined_df = pd.concat(results, ignore_index=True)

#                 # Convert DataFrame to CSV
#                 response = HttpResponse(content_type='text/csv')
#                 response['Content-Disposition'] = 'attachment; filename="updated_premium_file.csv"'

#                 combined_df.to_csv(path_or_buf=response, index=False)
#                 return response
#             else:
#                 return JsonResponse({'error': 'No data processed'}, status=400)

#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)
#     else:
#         return JsonResponse({'error': 'Invalid HTTP method'}, status=405)
# mapping_data_final = pd.concat([df for df in filtered_data.values()], axis=1)

#     # Serialize the final DataFrame and store it in the session
#     request.session['mapping_data_final'] = mapping_data_final.to_json(orient='split')
#     request.session.modified = True

def process_mapping_data(request):
    import json
    from django.http import JsonResponse, HttpResponse

    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')
        if not excel_file:
            return JsonResponse({'error': 'Excel file not found in request'}, status=400)

        mappings_data = request.POST.get('mappings')
        if not mappings_data:
            return JsonResponse({'error': 'Mappings data not provided'}, status=400)

        # Retrieve premium DataFrame from session
        new_df_json = request.session.get('new_df')
        if new_df_json:
            premium_df = pd.read_json(new_df_json, orient='split')
            print("The premiu_df is")
            print(premium_df.head())
        else:
            return JsonResponse({'error': 'Session does not contain premium data'}, status=500)

        try:
            mappings = json.loads(mappings_data)
            excel = pd.ExcelFile(excel_file)

            # Same mapping process as before
            for mapping in mappings:
                sheet_name = mapping['sheetName']
                sheet_df = pd.read_excel(excel, sheet_name=sheet_name)
                mapping_column_name = f'Mapping_{sheet_name}'

                if mapping_column_name in sheet_df.columns:
                    sheet_df = sheet_df[[sheet_name, mapping_column_name]]
                    premium_df = pd.merge(
                        premium_df, sheet_df, left_on=mapping['columnName'], right_on=sheet_name, how='left', suffixes=('', f'_{sheet_name}')
                    )
            request.session['mapping_data_final'] = premium_df.to_json(orient='split')
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="updated_premium_file.csv"'
            premium_df.to_csv(path_or_buf=response, index=False)
            return response
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid HTTP method'}, status=405)

