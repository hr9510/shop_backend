export const HandleChange = (e, userData, setUserData) => {
  const { name, value } = e.target;
  setUserData({
    ...userData,
    [name]: value,
  });
};
