const toMeddusaUrl = async () =>{

    try
    {
        const res = await axios.post('/medex',
        {timeout : 30000} //30 sec
        );

        location.replace(res.data.meddusaUrl);

    } catch (error) {useModal('Failed to load Meddusa: connection refused');}

}


const openInMedex = async function () {

   if (!props.total_cohorts)

    useNotification('Cohort does not exist.' );

    else

      if (!props.totalDocs) useNotification('Cohort is empty.' );

      else
        try
        {
          useLoading(true);
          var lmodal_title = document.querySelector('.lmodal__title');
          const id = props.session.id;
          var reqid = uuid();
          const source = axios.CancelToken.source();
          const res = await  axios.post('/result/cases/set', //'/api/sendCases',
            {   data: {
                  session_id: id,
                  datetime:  moment(new Date()).format('YYYY-MM-DD hh:mm:ss A'),
                  cohort_id : props.current.id,
                  total: props.totalDocs,
                  fields: props.fields,
                  reqid : reqid
              }
            },
            {cancelToken: source.token},
            {timeout : 180000} // 3x60sec
            );
            if (lmodal_title.innerHTML === 'Search was canceled') {
              source.cancel("Search is canceled");
              useLoading(false);
            }
            else if (Object.keys(res.data.data).length !== 0 && res.data.data.reqid === reqid) {
              props.setSessionState(res.data.data.session_id, []);
              useLoading(false);
              setTimeout(function(){
                location.replace(res.data.medexUrl);
              }, 3000)
            }
        } catch (error) {
            useLoading(false);
            errorHandling(error);}
  }